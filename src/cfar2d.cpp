#include "cfar2d.hpp"

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstring>

#if defined(__AVX2__)
#  include <immintrin.h>
#endif

namespace {

// log10 with a tiny floor to avoid -inf for zero/denormal inputs.
inline float to_db(float x) noexcept {
    return 10.0f * std::log10(x + 1.0e-30f);
}

// -----------------------------------------------------------------------------
// SIMD primitive: count how many floats in [p, p+n) are strictly less than v.
// Hot inner of OS-CFAR rank-only detection (see comment block in run_kernel_).
// -----------------------------------------------------------------------------
#if defined(__AVX2__)
inline int count_lt_simd(const float* p, int n, float v) noexcept {
    int count = 0;
    int i = 0;
    const __m256 vv = _mm256_set1_ps(v);
    // 32-wide unrolled body: 4 × AVX2 vectors per iter.
    for (; i + 32 <= n; i += 32) {
        __m256 x0 = _mm256_loadu_ps(p + i + 0);
        __m256 x1 = _mm256_loadu_ps(p + i + 8);
        __m256 x2 = _mm256_loadu_ps(p + i + 16);
        __m256 x3 = _mm256_loadu_ps(p + i + 24);
        int m0 = _mm256_movemask_ps(_mm256_cmp_ps(x0, vv, _CMP_LT_OQ));
        int m1 = _mm256_movemask_ps(_mm256_cmp_ps(x1, vv, _CMP_LT_OQ));
        int m2 = _mm256_movemask_ps(_mm256_cmp_ps(x2, vv, _CMP_LT_OQ));
        int m3 = _mm256_movemask_ps(_mm256_cmp_ps(x3, vv, _CMP_LT_OQ));
        count += __builtin_popcount(m0) + __builtin_popcount(m1) +
                 __builtin_popcount(m2) + __builtin_popcount(m3);
    }
    for (; i + 8 <= n; i += 8) {
        __m256 x = _mm256_loadu_ps(p + i);
        int m = _mm256_movemask_ps(_mm256_cmp_ps(x, vv, _CMP_LT_OQ));
        count += __builtin_popcount(m);
    }
    for (; i < n; ++i) {
        count += (p[i] < v) ? 1 : 0;
    }
    return count;
}
#else
inline int count_lt_simd(const float* p, int n, float v) noexcept {
    int count = 0;
    for (int i = 0; i < n; ++i) count += (p[i] < v) ? 1 : 0;
    return count;
}
#endif

} // namespace

// -----------------------------------------------------------------------------
// CFAR2D — construction / params
// -----------------------------------------------------------------------------
CFAR2D::CFAR2D(const CFAR2DParams& p) : params_(p) {
    recompute_derived_();
    const int outer = (2 * params_.N_ref_f + 2 * params_.N_guard_f + 1) *
                      (2 * params_.N_ref_t + 2 * params_.N_guard_t + 1);
    scratch_.reserve(static_cast<size_t>(outer));
    dets_.reserve(4096);
}

void CFAR2D::set_params(const CFAR2DParams& p) {
    params_ = p;
    recompute_derived_();
    const int outer = (2 * params_.N_ref_f + 2 * params_.N_guard_f + 1) *
                      (2 * params_.N_ref_t + 2 * params_.N_guard_t + 1);
    if (static_cast<int>(scratch_.capacity()) < outer) {
        scratch_.reserve(static_cast<size_t>(outer));
    }
}

void CFAR2D::recompute_derived_() {
    const int outer_w_f = 2 * params_.N_ref_f + 2 * params_.N_guard_f + 1;
    const int outer_w_t = 2 * params_.N_ref_t + 2 * params_.N_guard_t + 1;
    const int guard_w_f = 2 * params_.N_guard_f + 1;
    const int guard_w_t = 2 * params_.N_guard_t + 1;
    full_N_train_ = outer_w_f * outer_w_t - guard_w_f * guard_w_t;
    int k = static_cast<int>(std::lround(static_cast<double>(params_.rank_percent) *
                                         static_cast<double>(full_N_train_)));
    if (k < 0)                       k = 0;
    if (k > full_N_train_ - 1)       k = full_N_train_ - 1;
    full_k_     = k;
    alpha_lin_  = std::pow(10.0f, params_.threshold_db / 10.0f);
}

double CFAR2D::throughput_ms() const noexcept {
    return last_throughput_ms_;
}

// -----------------------------------------------------------------------------
// Inner kernel
// -----------------------------------------------------------------------------
// Per the spec the detection rule is:
//     T  = α · X(k)                            (linear power)
//     detect  ⇔  CUT > T  ⇔  X(k) < CUT/α
//
// X(k) is the k-th smallest of the N_train reference cells. The naïve approach
// runs std::nth_element on the gathered reference set for every CUT, which is
// O(N) per cell but with a large constant (~5 µs for N=816 in libstdc++).
// At 1 M CUTs that is ~5 s — single-threaded ~0.2 MS/s, parallel ~4 MS/s.
//
// Key insight (algorithmically equivalent to the spec): we do not need the
// exact X(k) to decide detection. We only need to know whether X(k) is below
// the scalar threshold V = CUT/α. Sorting facts:
//     X(k) <  V   ⇔   count(refs < V) >  k       (strict)
// So the detection decision reduces to a SIMD vector compare-and-count against
// a scalar threshold — ~10× faster than a full nth_element, with no gather
// required (we can scan the matrix in-place across reference cells).
//
// We only fall back to a true nth_element when a CUT passes the count check,
// because we still need the exact X(k) to compute snr_db = CUT_dB − X(k)_dB.
// Detections are sparse (~10⁻⁴ of cells in AWGN at Pfa ≤ 1%), so the expensive
// branch fires very rarely.
// -----------------------------------------------------------------------------
void CFAR2D::run_kernel_(const float* power, int rows, int cols,
                         int t_begin, int t_end,
                         std::vector<Detection>& out) {
    if (rows <= 0 || cols <= 0) return;

    const int   Nrf      = params_.N_ref_f;
    const int   Nrt      = params_.N_ref_t;
    const int   Ngf      = params_.N_guard_f;
    const int   Ngt      = params_.N_guard_t;
    const int   Wf       = Nrf + Ngf;             // half-window freq
    const int   Wt       = Nrt + Ngt;             // half-window time
    const float min_snr  = params_.min_snr_db;
    const float alpha    = alpha_lin_;
    const float inv_alpha = 1.0f / alpha;
    const float rank_pc  = params_.rank_percent;

    const int  full_N    = full_N_train_;
    const int  full_k    = full_k_;
    const int  side_seg  = Wf - Ngf;              // reference width per side of the guard band
    const int  full_row  = 2 * Wf + 1;            // outer freq width

    // Min reference count for edge cells. Below this the noise estimate is too
    // unstable to keep — drop CUT (spec §57: truncation is OK for interior).
    const int  min_refs  = std::max(16, full_N / 2);

    // Scratch sizing for the interior nth_element fallback.
    if (static_cast<int>(scratch_.size()) < full_N) {
        scratch_.resize(static_cast<size_t>(full_N));
    }

    for (int t = t_begin; t < t_end; ++t) {
        const bool t_interior = (t >= Wt && t + Wt < rows);
        const int  t_lo       = t_interior ? (t - Wt) : std::max(0, t - Wt);
        const int  t_hi       = t_interior ? (t + Wt) : std::min(rows - 1, t + Wt);
        const int  t_g_lo     = std::max(0, t - Ngt);
        const int  t_g_hi     = std::min(rows - 1, t + Ngt);

        const float* row_t    = power + static_cast<ptrdiff_t>(t) * cols;

        for (int f = 0; f < cols; ++f) {
            const bool f_interior   = (f >= Wf && f + Wf < cols);
            const bool full_interior = t_interior && f_interior;

            const float cut = row_t[f];
            const float V   = cut * inv_alpha;    // X(k) must be < V for detection

            int N_train, k;
            int count = 0;

            if (full_interior) {
                // Interior fast path — direct in-matrix SIMD scan, no gather.
                // Rows above the guard band — full freq stretch.
                for (int tt = t_lo; tt < t_g_lo; ++tt) {
                    count += count_lt_simd(power + static_cast<ptrdiff_t>(tt) * cols + (f - Wf),
                                           full_row, V);
                }
                // Guard-band rows — two side segments (skip the guard freq band and CUT col).
                for (int tt = t_g_lo; tt <= t_g_hi; ++tt) {
                    const float* row = power + static_cast<ptrdiff_t>(tt) * cols;
                    count += count_lt_simd(row + (f - Wf),       side_seg, V);
                    count += count_lt_simd(row + (f + Ngf + 1),  side_seg, V);
                }
                // Rows below the guard band.
                for (int tt = t_g_hi + 1; tt <= t_hi; ++tt) {
                    count += count_lt_simd(power + static_cast<ptrdiff_t>(tt) * cols + (f - Wf),
                                           full_row, V);
                }
                N_train = full_N;
                k       = full_k;
            } else {
                // Edge slow path — clip window, gather references for both the count
                // and a possible nth_element call (cheaper to share scratch here).
                const int f_lo   = std::max(0, f - Wf);
                const int f_hi   = std::min(cols - 1, f + Wf);
                const int f_g_lo = std::max(0, f - Ngf);
                const int f_g_hi = std::min(cols - 1, f + Ngf);

                scratch_.clear();
                for (int tt = t_lo; tt <= t_hi; ++tt) {
                    const float* row = power + static_cast<ptrdiff_t>(tt) * cols;
                    const bool in_guard_t = (tt >= t_g_lo && tt <= t_g_hi);
                    if (in_guard_t) {
                        if (f_lo < f_g_lo) {
                            const int cnt = f_g_lo - f_lo;
                            const size_t off = scratch_.size();
                            scratch_.resize(off + static_cast<size_t>(cnt));
                            std::memcpy(scratch_.data() + off, row + f_lo,
                                        static_cast<size_t>(cnt) * sizeof(float));
                        }
                        if (f_g_hi + 1 <= f_hi) {
                            const int cnt = f_hi - f_g_hi;
                            const size_t off = scratch_.size();
                            scratch_.resize(off + static_cast<size_t>(cnt));
                            std::memcpy(scratch_.data() + off, row + f_g_hi + 1,
                                        static_cast<size_t>(cnt) * sizeof(float));
                        }
                    } else {
                        const int cnt = f_hi - f_lo + 1;
                        const size_t off = scratch_.size();
                        scratch_.resize(off + static_cast<size_t>(cnt));
                        std::memcpy(scratch_.data() + off, row + f_lo,
                                    static_cast<size_t>(cnt) * sizeof(float));
                    }
                }

                N_train = static_cast<int>(scratch_.size());
                if (N_train < min_refs) continue;   // truncated window too small

                k = static_cast<int>(std::lround(static_cast<double>(rank_pc) *
                                                 static_cast<double>(N_train)));
                if (k < 0)              k = 0;
                if (k > N_train - 1)    k = N_train - 1;

                count = count_lt_simd(scratch_.data(), N_train, V);
            }

            // Detection rule (rank-based, no full sort needed for the decision):
            //   X(k) < V  iff  count(refs < V) > k.
            if (count <= k) continue;

            // CUT passed CFAR — now compute exact X(k) for snr_db reporting.
            float Xk;
            if (full_interior) {
                // Need to materialize the scratch buffer for nth_element here.
                float* sp = scratch_.data();
                int n = 0;
                for (int tt = t_lo; tt < t_g_lo; ++tt) {
                    const float* row = power + static_cast<ptrdiff_t>(tt) * cols;
                    std::memcpy(sp + n, row + (f - Wf),
                                static_cast<size_t>(full_row) * sizeof(float));
                    n += full_row;
                }
                for (int tt = t_g_lo; tt <= t_g_hi; ++tt) {
                    const float* row = power + static_cast<ptrdiff_t>(tt) * cols;
                    std::memcpy(sp + n, row + (f - Wf),
                                static_cast<size_t>(side_seg) * sizeof(float));
                    n += side_seg;
                    std::memcpy(sp + n, row + (f + Ngf + 1),
                                static_cast<size_t>(side_seg) * sizeof(float));
                    n += side_seg;
                }
                for (int tt = t_g_hi + 1; tt <= t_hi; ++tt) {
                    const float* row = power + static_cast<ptrdiff_t>(tt) * cols;
                    std::memcpy(sp + n, row + (f - Wf),
                                static_cast<size_t>(full_row) * sizeof(float));
                    n += full_row;
                }
                std::nth_element(scratch_.begin(),
                                 scratch_.begin() + k,
                                 scratch_.begin() + n);
                Xk = scratch_[static_cast<size_t>(k)];
            } else {
                std::nth_element(scratch_.begin(),
                                 scratch_.begin() + k,
                                 scratch_.begin() + N_train);
                Xk = scratch_[static_cast<size_t>(k)];
            }

            const float cut_db = to_db(cut);
            const float xk_db  = to_db(Xk);
            const float snr_db = cut_db - xk_db;

            // Per spec §47: even after CFAR pass, reject low-SNR detections.
            // The threshold_db gate is implicit in the count rule (alpha encodes it),
            // but min_snr_db is a separate hard floor.
            if (snr_db < min_snr) continue;

            out.push_back(Detection{t, f, cut_db, snr_db});
        }
    }
}

std::vector<Detection> CFAR2D::process(const float* power, int rows, int cols) {
    dets_.clear();
    const auto t0 = std::chrono::steady_clock::now();
    run_kernel_(power, rows, cols, 0, rows, dets_);
    const auto t1 = std::chrono::steady_clock::now();

    const double sec     = std::chrono::duration<double>(t1 - t0).count();
    const double samples = static_cast<double>(rows) * static_cast<double>(cols);
    last_throughput_ms_  = (sec > 0.0) ? (samples / sec / 1.0e6) : 0.0;

    return dets_;
}

void CFAR2D::process_stripe(const float* power, int rows, int cols,
                            int row_begin, int row_end,
                            std::vector<Detection>& out) {
    if (row_begin < 0)    row_begin = 0;
    if (row_end   > rows) row_end   = rows;
    if (row_begin >= row_end) return;

    const auto t0 = std::chrono::steady_clock::now();
    run_kernel_(power, rows, cols, row_begin, row_end, out);
    const auto t1 = std::chrono::steady_clock::now();

    const double sec     = std::chrono::duration<double>(t1 - t0).count();
    const double samples = static_cast<double>(row_end - row_begin) *
                           static_cast<double>(cols);
    last_throughput_ms_  = (sec > 0.0) ? (samples / sec / 1.0e6) : 0.0;
}
