// 2D OS-CFAR — Stage 1 implementation per docs/cfar-spec.md (status: approved).
//
// Contract (spec lines 90-141):
//   - Input: row-major float32 power matrix (rows=time, cols=freq), linear scale (|FFT|^2).
//   - Output: vector<Detection> with time/freq indices, power_db, snr_db.
//   - dB conversion happens inside the class.
//   - k = round(rank_percent * N_train_total), computed internally from current params.
//   - Edge handling: truncate window (no detection from cells with too-few reference cells).
//   - Hot path: no new/malloc — scratch buffers are reserved up front.
//   - Thread-safety: 1 instance = 1 thread. Parallelism via tiling (multiple instances,
//     each handling a disjoint row stripe but reading the shared power matrix).

#pragma once

#include <cstdint>
#include <vector>

struct Detection {
    int   t_idx;      // time index in spectrogram
    int   f_idx;      // freq bin
    float power_db;   // CUT power, dB
    float snr_db;     // CUT - noise_estimate, dB
};

struct CFAR2DParams {
    int   N_ref_f      = 16;
    int   N_ref_t      = 8;
    int   N_guard_f    = 4;
    int   N_guard_t    = 2;
    float rank_percent = 0.75f;  // k = round(rank_percent * N_train_total)
    float threshold_db = 12.5f;  // Detection Gap (alpha in dB)
    float min_snr_db   = 7.0f;   // hard floor
};

class CFAR2D {
public:
    explicit CFAR2D(const CFAR2DParams& p);

    // Full-matrix processing. Returns detections by value (one-shot per call, not hot-path-per-cell).
    std::vector<Detection> process(const float* power, int rows, int cols);

    // Last measured throughput in MS/s (samples_processed / wall_seconds / 1e6).
    double throughput_ms() const noexcept;

    // Update parameters without reconstructing. Resizes scratch if needed.
    void set_params(const CFAR2DParams& p);

    // Extension (does not violate the spec contract — additive only).
    // Process only rows [row_begin, row_end) but with full-matrix read access so window
    // clipping happens only at the *true* matrix edges, not at stripe seams. Used by the
    // benchmark for tiled parallel processing (one CFAR2D instance per thread).
    void process_stripe(const float* power, int rows, int cols,
                        int row_begin, int row_end,
                        std::vector<Detection>& out);

    // Read-only view of current params (utility).
    const CFAR2DParams& params() const noexcept { return params_; }

private:
    void   recompute_derived_();
    void   run_kernel_(const float* power, int rows, int cols,
                       int t_begin, int t_end,
                       std::vector<Detection>& out);

    CFAR2DParams params_;
    double       last_throughput_ms_ = 0.0;

    // Scratch (per-instance, reused across cells / calls).
    std::vector<float>     scratch_;
    std::vector<Detection> dets_;

    // Derived from params_, refreshed on construction and set_params().
    float alpha_lin_       = 1.0f;  // 10^(threshold_db/10)
    int   full_N_train_    = 0;     // reference-cell count for fully-interior CUT
    int   full_k_          = 0;     // k for fully-interior CUT
};
