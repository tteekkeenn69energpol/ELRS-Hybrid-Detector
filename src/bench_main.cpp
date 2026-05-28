// Inline micro-benchmark for the 2D OS-CFAR implementation.
//
// Targets the spec figure ≥ 80 MS/s on a synthetic 512 (time) × 2048 (freq)
// power spectrogram. Runs:
//   1. Single-threaded baseline (CFAR2D::process)
//   2. Tiled multi-threaded (one CFAR2D per thread, process_stripe)
//
// Compile via the project CMakeLists.txt (Release, -O3 -mavx2 -march=native).

#include "cfar2d.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <random>
#include <thread>
#include <vector>

namespace {

constexpr int kRows = 512;
constexpr int kCols = 2048;

// Generate an AWGN-like spectrogram with a few synthetic chirp injections.
// We do NOT need this to be physically calibrated — the benchmark measures
// throughput, not detection quality. Test/QA owns Pfa/Pd validation.
std::vector<float> make_synthetic(int rows, int cols) {
    std::vector<float> power(static_cast<size_t>(rows) * cols);
    std::mt19937 rng(42);
    std::normal_distribution<float> nd(0.0f, 1.0f);

    // Rayleigh-distributed background power = (|I|^2 + |Q|^2) for unit-variance I/Q.
    for (size_t i = 0; i < power.size(); ++i) {
        const float a = nd(rng);
        const float b = nd(rng);
        power[i] = a * a + b * b;     // mean ~= 2
    }

    // Inject a handful of synthetic chirps: diagonal ridges in (t, f).
    const float chirp_power = 60.0f;  // ~14.8 dB above mean noise
    for (int c = 0; c < 8; ++c) {
        const int t0   = 30 + c * 55;
        const int f0   = 100 + c * 230;
        const int slope = 1 + (c % 3);
        for (int dt = 0; dt < 40; ++dt) {
            const int tt = t0 + dt;
            const int ff = f0 + dt * slope;
            if (tt < rows && ff < cols && ff >= 0) {
                power[static_cast<size_t>(tt) * cols + ff] += chirp_power;
            }
        }
    }
    return power;
}

struct BenchResult {
    double   wall_ms;
    double   ms_per_sec;        // MS/s
    size_t   detections;
};

BenchResult bench_single(const std::vector<float>& power, int rows, int cols, int iters) {
    CFAR2DParams p;  // defaults from spec
    CFAR2D cfar(p);

    // Warm-up: prime caches, JIT branch predictor, allocate dets vector capacity.
    auto dets = cfar.process(power.data(), rows, cols);

    const auto t0 = std::chrono::steady_clock::now();
    size_t total_dets = 0;
    for (int i = 0; i < iters; ++i) {
        dets = cfar.process(power.data(), rows, cols);
        total_dets += dets.size();
    }
    const auto t1 = std::chrono::steady_clock::now();

    const double sec = std::chrono::duration<double>(t1 - t0).count();
    const double samples = static_cast<double>(rows) * static_cast<double>(cols) * iters;

    BenchResult r;
    r.wall_ms     = sec * 1000.0 / iters;
    r.ms_per_sec  = samples / sec / 1.0e6;
    r.detections  = total_dets / static_cast<size_t>(iters);
    return r;
}

BenchResult bench_parallel(const std::vector<float>& power, int rows, int cols,
                            int iters, int nthreads) {
    CFAR2DParams p;

    // Build per-thread CFAR2D instances up front (one instance = one thread, per spec).
    std::vector<CFAR2D> cfar;
    cfar.reserve(static_cast<size_t>(nthreads));
    for (int i = 0; i < nthreads; ++i) cfar.emplace_back(p);

    // Stripe boundaries.
    std::vector<int> bounds(static_cast<size_t>(nthreads) + 1);
    for (int i = 0; i <= nthreads; ++i) {
        bounds[i] = static_cast<int>(static_cast<int64_t>(rows) * i / nthreads);
    }

    // Per-thread output buffers (reused across iters).
    std::vector<std::vector<Detection>> outs(static_cast<size_t>(nthreads));
    for (auto& v : outs) v.reserve(1024);

    // Warm-up.
    {
        std::vector<std::thread> th;
        th.reserve(static_cast<size_t>(nthreads));
        for (int i = 0; i < nthreads; ++i) {
            th.emplace_back([&, i] {
                outs[i].clear();
                cfar[i].process_stripe(power.data(), rows, cols,
                                       bounds[i], bounds[i + 1], outs[i]);
            });
        }
        for (auto& t : th) t.join();
    }

    const auto t0 = std::chrono::steady_clock::now();
    size_t total_dets = 0;
    for (int it = 0; it < iters; ++it) {
        std::vector<std::thread> th;
        th.reserve(static_cast<size_t>(nthreads));
        for (int i = 0; i < nthreads; ++i) {
            th.emplace_back([&, i] {
                outs[i].clear();
                cfar[i].process_stripe(power.data(), rows, cols,
                                       bounds[i], bounds[i + 1], outs[i]);
            });
        }
        for (auto& t : th) t.join();
        for (auto& v : outs) total_dets += v.size();
    }
    const auto t1 = std::chrono::steady_clock::now();

    const double sec = std::chrono::duration<double>(t1 - t0).count();
    const double samples = static_cast<double>(rows) * static_cast<double>(cols) * iters;

    BenchResult r;
    r.wall_ms     = sec * 1000.0 / iters;
    r.ms_per_sec  = samples / sec / 1.0e6;
    r.detections  = total_dets / static_cast<size_t>(iters);
    return r;
}

} // namespace

int main(int argc, char** argv) {
    int rows    = kRows;
    int cols    = kCols;
    int iters   = 5;
    int threads = static_cast<int>(std::thread::hardware_concurrency());
    if (threads <= 0) threads = 8;

    // Tiny CLI: rows cols iters threads
    if (argc > 1) rows    = std::atoi(argv[1]);
    if (argc > 2) cols    = std::atoi(argv[2]);
    if (argc > 3) iters   = std::atoi(argv[3]);
    if (argc > 4) threads = std::atoi(argv[4]);

    std::printf("CFAR2D bench: %d x %d  iters=%d  threads=%d\n",
                rows, cols, iters, threads);
    std::printf("Params: N_ref_f=16 N_ref_t=8 N_guard_f=4 N_guard_t=2 "
                "rank=0.75 (k=612) thr_db=12.5 min_snr_db=7.0\n");

    auto power = make_synthetic(rows, cols);

    auto r1 = bench_single(power, rows, cols, iters);
    std::printf("\n[single]   wall=%.2f ms/iter  throughput=%.2f MS/s  dets/iter=%zu\n",
                r1.wall_ms, r1.ms_per_sec, r1.detections);

    auto r2 = bench_parallel(power, rows, cols, iters, threads);
    std::printf("[parallel] wall=%.2f ms/iter  throughput=%.2f MS/s  dets/iter=%zu  (T=%d)\n",
                r2.wall_ms, r2.ms_per_sec, r2.detections, threads);

    const bool pass = (r2.ms_per_sec >= 80.0);
    std::printf("\nTarget ≥ 80 MS/s: %s  (parallel=%.2f MS/s)\n",
                pass ? "PASS" : "FAIL", r2.ms_per_sec);

    return pass ? 0 : 1;
}
