"""Test/QA driver for 2D OS-CFAR (Stage 1) per cfar-spec.md.

Implements T-1..T-6 from the agent prompt:
  T-1  synthetic AWGN + ELRS chirp data (see synth.py)
  T-2  Pfa Monte-Carlo + analytic cross-check
  T-3  ROC curve (Pfa, Pd) for an SNR sweep
  T-4  throughput benchmark (single + parallel, independent of bench_main.cpp)
  T-5  results emitted to /tests/test-results.{md,json,png}
  T-6  PASS / FAIL verdict
"""

import json
import os
import sys
import time
from dataclasses import asdict

import numpy as np

# Local imports
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import synth
from cfar2d_py import CFAR2DParams, CFAR2D, process_parallel


# -----------------------------------------------------------------------------
# Analytic Pfa (cfar-spec §45):
#   P_fa = Π_{i=1..k} (N+1-i)/(N+1-i+α)
# -----------------------------------------------------------------------------
def analytic_pfa(N: int, k: int, alpha_lin: float) -> float:
    logp = 0.0
    for i in range(1, k + 1):
        num = (N + 1 - i)
        den = (N + 1 - i + alpha_lin)
        logp += np.log(num) - np.log(den)
    return float(np.exp(logp))


# -----------------------------------------------------------------------------
# T-2: Pfa Monte-Carlo on AWGN-only.
# -----------------------------------------------------------------------------
def measure_pfa_mc(params: CFAR2DParams, n_matrices: int = 10,
                   n_frames: int = 512, sigma: float = 1.0,
                   seed: int = 12345, nthreads: int = 16,
                   verbose: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    total_cells = 0
    total_dets  = 0
    t_total = 0.0
    for i in range(n_matrices):
        P = synth.make_awgn_matrix(n_frames, sigma, rng)
        t0 = time.time()
        n, _, _ = process_parallel(P, params, nthreads=nthreads)
        t_total += (time.time() - t0)
        total_cells += P.size
        total_dets  += n
        if verbose:
            print(f"  Pfa MC [{i + 1}/{n_matrices}]  cells={P.size}  dets={n}  cum_pfa={total_dets/total_cells:.4e}")
    pfa_mc = total_dets / total_cells if total_cells > 0 else 0.0
    return {
        "n_matrices": n_matrices,
        "n_frames":   n_frames,
        "n_total":    total_cells,
        "n_dets":     total_dets,
        "pfa_mc":     pfa_mc,
        "wall_sec":   t_total,
        "params":     asdict(params),
    }


# -----------------------------------------------------------------------------
# T-3 & Pd: per-packet Pd at fixed threshold or sweep.
# Each packet is one (256, 2048) spectrogram with one chirp preamble + AWGN.
# A packet is "detected" if ≥ tol detections fall inside the preamble frame window.
# -----------------------------------------------------------------------------
def measure_pd_at_snr(params: CFAR2DParams, snr_db: float, n_packets: int = 1000,
                      n_frames: int = 256, sigma: float = 1.0,
                      seed: int = 4242, nthreads: int = 16,
                      tol_in_window: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    n_detected = 0
    n_dets_in  = 0
    n_dets_out = 0
    for i in range(n_packets):
        P, (fl, fh) = synth.make_packet_matrix(n_frames, sigma, snr_db, rng)
        # Single-thread is faster than parallel on these small matrices
        # (thread launch overhead dominates).
        cfar = _get_cfar(params)
        n_total, _, dets = cfar.process(P)
        # Decide detection.
        in_win = sum(1 for d in dets if fl <= d.t_idx <= fh)
        out_win = n_total - in_win
        if in_win >= tol_in_window:
            n_detected += 1
        n_dets_in  += in_win
        n_dets_out += out_win
    pd = n_detected / n_packets if n_packets > 0 else 0.0
    return {
        "snr_db":      snr_db,
        "n_packets":   n_packets,
        "n_detected":  n_detected,
        "pd":          pd,
        "n_dets_in":   n_dets_in,
        "n_dets_out":  n_dets_out,
        "n_frames":    n_frames,
    }


# Singleton CFAR per params hash to avoid recreating on every packet.
_CFAR_CACHE = {}
def _get_cfar(params: CFAR2DParams) -> CFAR2D:
    key = (params.N_ref_f, params.N_ref_t, params.N_guard_f, params.N_guard_t,
           round(params.rank_percent, 5), round(params.threshold_db, 5),
           round(params.min_snr_db, 5))
    c = _CFAR_CACHE.get(key)
    if c is None:
        c = CFAR2D(params)
        _CFAR_CACHE[key] = c
    return c


# -----------------------------------------------------------------------------
# T-3: ROC sweep — for each SNR, sweep threshold_db, record (Pfa, Pd).
# Strategy: pre-compute spectrograms once per SNR, re-CFAR with each threshold.
# -----------------------------------------------------------------------------
def roc_sweep(base_params: CFAR2DParams,
              snrs_db, thresholds_db,
              n_packets_per_snr: int = 100,
              n_awgn_matrices: int = 4, awgn_frames: int = 512,
              n_frames_per_packet: int = 256,
              sigma: float = 1.0, seed: int = 9999, nthreads: int = 16,
              verbose: bool = True) -> dict:
    # Pre-generate AWGN matrices (one-shot).
    if verbose:
        print(f"[ROC] pre-generating {n_awgn_matrices} AWGN matrices  ({awgn_frames}×{synth.FFT_SIZE} each)")
    rng_awgn = np.random.default_rng(seed)
    awgn_mats = [synth.make_awgn_matrix(awgn_frames, sigma, rng_awgn) for _ in range(n_awgn_matrices)]
    awgn_total = sum(m.size for m in awgn_mats)

    # Pre-generate packets per SNR.
    if verbose:
        print(f"[ROC] pre-generating {n_packets_per_snr} packets × {len(snrs_db)} SNRs ...")
    packets = {}
    rng_sig = np.random.default_rng(seed + 1)
    for s in snrs_db:
        pkt_list = []
        for _ in range(n_packets_per_snr):
            P, win = synth.make_packet_matrix(n_frames_per_packet, sigma, s, rng_sig)
            pkt_list.append((P, win))
        packets[s] = pkt_list
        if verbose:
            print(f"  [ROC] SNR={float(s):+5.1f}dB  {len(pkt_list)} packets ready")

    # Sweep threshold.
    out_rows = []
    pfa_for_thr = {}
    for thr in thresholds_db:
        p = CFAR2DParams(
            N_ref_f=base_params.N_ref_f, N_ref_t=base_params.N_ref_t,
            N_guard_f=base_params.N_guard_f, N_guard_t=base_params.N_guard_t,
            rank_percent=base_params.rank_percent,
            threshold_db=float(thr),
            min_snr_db=base_params.min_snr_db,
        )
        # Pfa on shared AWGN set.
        n_det_awgn = 0
        for M in awgn_mats:
            n, _, _ = process_parallel(M, p, nthreads=nthreads)
            n_det_awgn += n
        pfa_mc = n_det_awgn / awgn_total
        pfa_for_thr[thr] = pfa_mc

        # Pd per SNR for this threshold.
        for s in snrs_db:
            cfar = _get_cfar(p)
            n_detected = 0
            for (P, (fl, fh)) in packets[s]:
                n_total, _, dets = cfar.process(P)
                in_win = sum(1 for d in dets if fl <= d.t_idx <= fh)
                if in_win >= 1:
                    n_detected += 1
            pd = n_detected / n_packets_per_snr
            out_rows.append({"thr_db": float(thr), "snr_db": float(s),
                             "pfa": pfa_mc, "pd": pd})
        if verbose:
            print(f"  [ROC] thr={thr:5.2f} dB  pfa={pfa_mc:.4e}")

    return {
        "snrs_db": list(map(float, snrs_db)),
        "thresholds_db": list(map(float, thresholds_db)),
        "n_packets_per_snr": n_packets_per_snr,
        "n_awgn_matrices": n_awgn_matrices,
        "awgn_frames": awgn_frames,
        "rows": out_rows,
        "pfa_for_thr": pfa_for_thr,
    }


# -----------------------------------------------------------------------------
# T-4: Throughput benchmark — independent of bench_main.cpp.
# Generates its own synthetic spectrogram. 10 iters, take median.
# -----------------------------------------------------------------------------
def throughput_bench(params: CFAR2DParams, rows: int = 512, cols: int = 2048,
                     iters: int = 10, sigma: float = 1.0, seed: int = 7,
                     nthreads: int = None) -> dict:
    if nthreads is None:
        nthreads = os.cpu_count() or 8

    rng = np.random.default_rng(seed)
    # Build one realistic spectrogram (AWGN + a couple of injected chirps).
    P, _ = synth.make_packet_matrix(rows, sigma, snr_db=+3.0, rng=rng)
    if P.shape != (rows, cols):
        # synth fixes cols=FFT_SIZE; for non-matching cols we crop/pad.
        if P.shape[1] >= cols:
            P = np.ascontiguousarray(P[:, :cols])
        else:
            pad = np.zeros((P.shape[0], cols - P.shape[1]), dtype=np.float32)
            P = np.ascontiguousarray(np.concatenate([P, pad], axis=1))

    # Single-thread (uses class instance).
    cfar = CFAR2D(params)
    _, _, _ = cfar.process(P)              # warm-up
    single_ms = []
    for _ in range(iters):
        n, th, _ = cfar.process(P)
        single_ms.append(th)

    # Parallel — one call per iter creates threads internally.
    process_parallel(P, params, nthreads=nthreads)  # warm-up
    parallel_ms = []
    for _ in range(iters):
        n, th, _ = process_parallel(P, params, nthreads=nthreads)
        parallel_ms.append(th)

    return {
        "rows":         rows,
        "cols":         cols,
        "iters":        iters,
        "nthreads":     nthreads,
        "single_med":   float(np.median(single_ms)),
        "single_mean":  float(np.mean(single_ms)),
        "single_min":   float(np.min(single_ms)),
        "single_max":   float(np.max(single_ms)),
        "parallel_med": float(np.median(parallel_ms)),
        "parallel_mean": float(np.mean(parallel_ms)),
        "parallel_min": float(np.min(parallel_ms)),
        "parallel_max": float(np.max(parallel_ms)),
        "single_all":   list(map(float, single_ms)),
        "parallel_all": list(map(float, parallel_ms)),
    }


# -----------------------------------------------------------------------------
# Main entry — orchestrates T-1 .. T-6.
# -----------------------------------------------------------------------------
def main():
    out_json = os.path.join(HERE, "test-results.json")
    out_md   = os.path.join(HERE, "test-results.md")
    out_png  = os.path.join(HERE, "test-results.png")

    params = CFAR2DParams()  # spec defaults
    nthreads = os.cpu_count() or 16

    print("=" * 72)
    print("Stage-1 Test/QA — 2D OS-CFAR")
    print("=" * 72)
    print(f"Spec params: N_ref_f={params.N_ref_f} N_ref_t={params.N_ref_t} "
          f"N_guard_f={params.N_guard_f} N_guard_t={params.N_guard_t} "
          f"rank_pc={params.rank_percent} thr_db={params.threshold_db} "
          f"min_snr_db={params.min_snr_db}")
    print(f"Derived:     N_train={params.N_train_total}  k={params.k}  "
          f"alpha_lin={params.alpha_lin:.4f}")
    pfa_analytic = analytic_pfa(params.N_train_total, params.k, params.alpha_lin)
    print(f"Analytic Pfa (spec §45): {pfa_analytic:.4e}")
    print()

    # ------------------------------------------------------------------ T-2
    print("[T-2] Pfa Monte-Carlo  (10 × 512×2048 AWGN matrices)")
    pfa_res = measure_pfa_mc(params, n_matrices=10, n_frames=512,
                              sigma=1.0, seed=12345, nthreads=nthreads)
    pfa_res["pfa_analytic"] = pfa_analytic
    print(f"  → Pfa(MC)      = {pfa_res['pfa_mc']:.4e}")
    print(f"    Pfa(analytic) = {pfa_analytic:.4e}")
    if pfa_analytic > 0:
        rel = abs(pfa_res['pfa_mc'] - pfa_analytic) / pfa_analytic
        print(f"    |MC-analytic|/analytic = {rel:.2%}")
    print(f"  → N_total = {pfa_res['n_total']:,}   N_det = {pfa_res['n_dets']:,}")
    print(f"  → wall    = {pfa_res['wall_sec']:.2f}s  (CFAR only)")
    pfa_pass = pfa_res['pfa_mc'] <= 0.01
    print(f"  Gate Pfa ≤ 1%: {'PASS' if pfa_pass else 'FAIL'}")
    print()

    # ------------------------------------------------------------------ T-3
    print("[T-3] ROC sweep + Pd vs SNR (default threshold = 12.5 dB)")
    snrs_pd = list(range(-12, 11, 2))   # -12 .. +10 step 2
    pd_rows = []
    for s in snrs_pd:
        r = measure_pd_at_snr(params, snr_db=float(s), n_packets=200,
                              n_frames=256, sigma=1.0, seed=4242 + s,
                              nthreads=nthreads)
        pd_rows.append(r)
        print(f"  Pd@{s:+3d}dB = {r['pd']:.3f}  ({r['n_detected']}/{r['n_packets']})  "
              f"dets_in/out = {r['n_dets_in']}/{r['n_dets_out']}")

    print()
    print("[T-3] ROC curve (threshold sweep for selected SNRs)")
    roc_snrs = [-12.0, -9.0, -6.0, -3.0, 0.0, 3.0, 6.0]
    roc_thrs = [6.0, 8.0, 10.0, 11.0, 12.0, 12.5, 13.0, 14.0, 16.0, 18.0, 20.0]
    roc_res = roc_sweep(params, roc_snrs, roc_thrs,
                        n_packets_per_snr=100,
                        n_awgn_matrices=4, awgn_frames=512,
                        n_frames_per_packet=256,
                        sigma=1.0, seed=9999, nthreads=nthreads)

    # ------------------------------------------------------------------ T-4
    print()
    print(f"[T-4] Throughput benchmark  (512×2048, 10 iters, {nthreads} threads)")
    th_res = throughput_bench(params, rows=512, cols=2048, iters=10,
                              sigma=1.0, nthreads=nthreads)
    print(f"  Single  median = {th_res['single_med']:.2f} MS/s  "
          f"(min {th_res['single_min']:.2f} max {th_res['single_max']:.2f})")
    print(f"  Parallel median = {th_res['parallel_med']:.2f} MS/s  "
          f"(min {th_res['parallel_min']:.2f} max {th_res['parallel_max']:.2f})  "
          f"[T={th_res['nthreads']}]")
    thr_pass = th_res['parallel_med'] >= 80.0
    print(f"  Gate Throughput ≥ 80 MS/s: {'PASS' if thr_pass else 'FAIL'}")

    # ------------------------------------------------------------------ Summary
    verdict = (pfa_pass and thr_pass)
    print()
    print("=" * 72)
    print(f"VERDICT: {'PASS' if verdict else 'FAIL'}   "
          f"(Pfa {'≤' if pfa_pass else '>'} 1%, "
          f"Thrpt {'≥' if thr_pass else '<'} 80 MS/s)")
    print("=" * 72)

    # ------------------------------------------------------------------ JSON dump
    out = {
        "spec_params":   asdict(params),
        "params_derived": {
            "N_train_total": params.N_train_total,
            "k":             params.k,
            "alpha_lin":     params.alpha_lin,
        },
        "pfa_analytic":  pfa_analytic,
        "pfa_mc":        pfa_res,
        "pd_vs_snr":     pd_rows,
        "roc":           roc_res,
        "throughput":    th_res,
        "verdict":       "PASS" if verdict else "FAIL",
        "pfa_pass":      bool(pfa_pass),
        "thrpt_pass":    bool(thr_pass),
    }
    with open(out_json, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults JSON written → {out_json}")

    return out


if __name__ == "__main__":
    main()
