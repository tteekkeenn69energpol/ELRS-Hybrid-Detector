// C ABI wrapper around CFAR2D for ctypes-based testing.
// Read-only access to /src/cfar2d.hpp + cfar2d.cpp — no modification of the
// implementation (Test/QA contract: bugs go back to C++ Dev).

#include "../src/cfar2d.hpp"

#include <algorithm>
#include <cstdint>
#include <thread>
#include <vector>

extern "C" {

struct DetectionC {
    int32_t t_idx;
    int32_t f_idx;
    float   power_db;
    float   snr_db;
};

void* cfar2d_create(int Nrf, int Nrt, int Ngf, int Ngt,
                    float rank_pc, float thr_db, float min_snr_db) {
    CFAR2DParams p;
    p.N_ref_f      = Nrf;
    p.N_ref_t      = Nrt;
    p.N_guard_f    = Ngf;
    p.N_guard_t    = Ngt;
    p.rank_percent = rank_pc;
    p.threshold_db = thr_db;
    p.min_snr_db   = min_snr_db;
    return new CFAR2D(p);
}

void cfar2d_destroy(void* handle) {
    delete static_cast<CFAR2D*>(handle);
}

void cfar2d_set_params(void* handle, int Nrf, int Nrt, int Ngf, int Ngt,
                       float rank_pc, float thr_db, float min_snr_db) {
    CFAR2DParams p;
    p.N_ref_f      = Nrf;
    p.N_ref_t      = Nrt;
    p.N_guard_f    = Ngf;
    p.N_guard_t    = Ngt;
    p.rank_percent = rank_pc;
    p.threshold_db = thr_db;
    p.min_snr_db   = min_snr_db;
    static_cast<CFAR2D*>(handle)->set_params(p);
}

// Returns total detections produced. If > out_cap, only the first out_cap are
// copied into `out` (overflow is reported via the return value, not silently lost).
int32_t cfar2d_process(void* handle, const float* power, int rows, int cols,
                       DetectionC* out, int32_t out_cap, double* thrpt_out) {
    CFAR2D* c = static_cast<CFAR2D*>(handle);
    auto dets = c->process(power, rows, cols);
    if (thrpt_out) *thrpt_out = c->throughput_ms();
    const int32_t total = static_cast<int32_t>(dets.size());
    const int32_t n = std::min<int32_t>(total, out_cap);
    for (int32_t i = 0; i < n; ++i) {
        out[i].t_idx    = dets[static_cast<size_t>(i)].t_idx;
        out[i].f_idx    = dets[static_cast<size_t>(i)].f_idx;
        out[i].power_db = dets[static_cast<size_t>(i)].power_db;
        out[i].snr_db   = dets[static_cast<size_t>(i)].snr_db;
    }
    return total;
}

// Parallel tiled processing: one CFAR2D instance per thread, each handling a
// disjoint row stripe with full-matrix read access (window clipping only at
// true matrix edges, not stripe seams). Returns aggregate detection count.
// Reports aggregate throughput (samples / wall_seconds / 1e6).
int32_t cfar2d_process_parallel(int Nrf, int Nrt, int Ngf, int Ngt,
                                float rank_pc, float thr_db, float min_snr_db,
                                const float* power, int rows, int cols,
                                int nthreads,
                                DetectionC* out, int32_t out_cap,
                                double* thrpt_out) {
    if (nthreads <= 0) nthreads = 1;
    CFAR2DParams p;
    p.N_ref_f      = Nrf;
    p.N_ref_t      = Nrt;
    p.N_guard_f    = Ngf;
    p.N_guard_t    = Ngt;
    p.rank_percent = rank_pc;
    p.threshold_db = thr_db;
    p.min_snr_db   = min_snr_db;

    std::vector<CFAR2D> cfar;
    cfar.reserve(static_cast<size_t>(nthreads));
    for (int i = 0; i < nthreads; ++i) cfar.emplace_back(p);

    std::vector<int> bounds(static_cast<size_t>(nthreads) + 1);
    for (int i = 0; i <= nthreads; ++i) {
        bounds[static_cast<size_t>(i)] =
            static_cast<int>(static_cast<int64_t>(rows) * i / nthreads);
    }

    std::vector<std::vector<Detection>> outs(static_cast<size_t>(nthreads));
    for (auto& v : outs) v.reserve(1024);

    const auto t0 = std::chrono::steady_clock::now();
    std::vector<std::thread> th;
    th.reserve(static_cast<size_t>(nthreads));
    for (int i = 0; i < nthreads; ++i) {
        th.emplace_back([&, i] {
            outs[static_cast<size_t>(i)].clear();
            cfar[static_cast<size_t>(i)].process_stripe(
                power, rows, cols,
                bounds[static_cast<size_t>(i)],
                bounds[static_cast<size_t>(i) + 1],
                outs[static_cast<size_t>(i)]);
        });
    }
    for (auto& t : th) t.join();
    const auto t1 = std::chrono::steady_clock::now();

    const double sec     = std::chrono::duration<double>(t1 - t0).count();
    const double samples = static_cast<double>(rows) * static_cast<double>(cols);
    if (thrpt_out) *thrpt_out = (sec > 0.0) ? (samples / sec / 1.0e6) : 0.0;

    int32_t total = 0;
    int32_t written = 0;
    for (auto& v : outs) {
        for (auto& d : v) {
            if (written < out_cap) {
                out[written].t_idx    = d.t_idx;
                out[written].f_idx    = d.f_idx;
                out[written].power_db = d.power_db;
                out[written].snr_db   = d.snr_db;
                ++written;
            }
            ++total;
        }
    }
    return total;
}

} // extern "C"
