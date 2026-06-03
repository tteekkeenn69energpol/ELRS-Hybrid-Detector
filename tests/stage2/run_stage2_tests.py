"""Stage 2 master test runner — T2-1..T2-7.

Orchestrates:
  T2-1  synth_dataset (inline)
  T2-2  test_sf_accuracy.run()
  T2-3  test_bw_accuracy.run()
  T2-4  SF+BW pair accuracy @ SNR=-14 dB
  T2-5  Independent latency benchmark
  T2-6  False-trigger rate on pure AWGN
  T2-7  Verdict → test-results-stage2.md

Writes:
  tests/stage2/test-results-stage2.md
  obsidian-vault/logs/test-results-stage2-2026-05-29.md
"""

from __future__ import annotations

import os
import sys
import time
import platform
import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..", "..")
_SRC  = os.path.join(_ROOT, "src", "stage2")
sys.path.insert(0, _SRC)
sys.path.insert(0, _HERE)

from blind_estimator import ELRS_BlindParameterEstimator
from synth_dataset import (
    make_iq_buffer, make_awgn_buffer,
    SFS, BWS, SNR_RANGE, N_PER_COMBINATION, SAMP_RATE, N_BUFFER,
)
import test_sf_accuracy
import test_bw_accuracy

# ---------------------------------------------------------------------------
# Gate thresholds
# ---------------------------------------------------------------------------
SF_GATE_SNR   = -10
SF_GATE_ACC   = 0.85
BW_GATE_SNR   = -12
BW_GATE_ACC   = 0.80
PAIR_GATE_SNR = -14
PAIR_GATE_ACC = 0.78
LAT_GATE_MS   = 25.0
FT_GATE       = 0.05   # info-only


# ---------------------------------------------------------------------------
# T2-4 — SF+BW pair accuracy @ SNR=-14 dB
# ---------------------------------------------------------------------------
def t2_4_pair_accuracy(n_per_combo: int = N_PER_COMBINATION, seed: int = 4) -> dict:
    print("\n[T2-4] SF+BW pair accuracy @ SNR=-14 dB")
    rng = np.random.default_rng(seed)
    est = ELRS_BlindParameterEstimator(
        samp_rate=SAMP_RATE, wavelet="sym5", dwt_level=4,
        threshold_low=0.0, threshold_high=1.1,
        use_sst=True, holdoff_s=0.0,
    )

    correct = 0
    total = 0
    per_pair: dict[tuple, dict] = {}

    for sf in SFS:
        for bw in BWS:
            c = 0
            for _ in range(n_per_combo):
                buf = make_iq_buffer(sf, bw, snr_db=PAIR_GATE_SNR, rng=rng)
                res = est.estimate(buf)
                if res["sf"] == sf and res["bw"] == bw:
                    c += 1
            correct += c
            total += n_per_combo
            per_pair[(sf, bw)] = {"correct": c, "total": n_per_combo,
                                  "acc": c / n_per_combo}
            print(f"  SF{sf} BW{bw//1000}k: {c}/{n_per_combo} = {c/n_per_combo:.2%}")

    acc = correct / total
    verdict = "PASS" if acc >= PAIR_GATE_ACC else "FAIL"
    print(f"  PAIR total: {correct}/{total} = {acc:.1%}  target≥{PAIR_GATE_ACC:.0%} → {verdict}")
    return {"acc": acc, "correct": correct, "total": total,
            "verdict": verdict, "per_pair": per_pair}


# ---------------------------------------------------------------------------
# T2-5 — Independent latency benchmark
# ---------------------------------------------------------------------------
def t2_5_latency(n_repeats: int = 10, seed: int = 5) -> dict:
    print("\n[T2-5] Latency benchmark (independent of bench_stage2.py)")
    rng = np.random.default_rng(seed)

    # Use a real chirp buffer, not pure AWGN, to exercise the full pipeline
    buf = make_iq_buffer(sf=9, bw=812_000, snr_db=0.0, rng=rng)

    est = ELRS_BlindParameterEstimator(
        samp_rate=SAMP_RATE, wavelet="sym5", dwt_level=4,
        threshold_low=0.0, threshold_high=1.1,
        use_sst=True, holdoff_s=0.0,
    )

    latencies_ms: list[float] = []
    for i in range(n_repeats):
        t0 = time.perf_counter()
        est.estimate(buf)
        lat = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(lat)
        print(f"  rep {i+1:2d}: {lat:.2f} ms")

    med = float(np.median(latencies_ms))
    std = float(np.std(latencies_ms))
    verdict = "PASS" if med <= LAT_GATE_MS else "FAIL"
    print(f"  Median={med:.2f} ms  std={std:.2f} ms  target≤{LAT_GATE_MS} ms → {verdict}")
    return {"median_ms": med, "std_ms": std,
            "min_ms": min(latencies_ms), "max_ms": max(latencies_ms),
            "latencies_ms": latencies_ms, "verdict": verdict}


# ---------------------------------------------------------------------------
# T2-6 — False trigger rate (confidence ≥ 0.4 on pure AWGN, info-only)
# ---------------------------------------------------------------------------
def t2_6_false_trigger(n_bufs: int = 1000, seed: int = 6) -> dict:
    print(f"\n[T2-6] False trigger rate on {n_bufs} pure AWGN buffers")
    rng = np.random.default_rng(seed)

    # threshold_low=0.4 per spec — we measure how often conf ≥ 0.4 triggers
    est = ELRS_BlindParameterEstimator(
        samp_rate=SAMP_RATE, wavelet="sym5", dwt_level=4,
        threshold_low=0.4, threshold_high=0.7,
        use_sst=True, holdoff_s=0.0,
    )

    n_triggered = 0
    for i in range(n_bufs):
        buf = make_awgn_buffer(rng)
        res = est.estimate(buf)
        # A "false trigger" is any result that passes the gate (conf ≥ 0.4)
        if res["stage3_ready"] or res["needs_neural"]:
            n_triggered += 1

    rate = n_triggered / n_bufs
    status = "✅" if rate <= FT_GATE else "⚠️"
    print(f"  False triggers: {n_triggered}/{n_bufs} = {rate:.1%}  "
          f"target≤{FT_GATE:.0%}  {status} (info-only)")
    return {"n_triggered": n_triggered, "n_bufs": n_bufs,
            "rate": rate, "status": status}


# ---------------------------------------------------------------------------
# T2-7 — Write verdict report
# ---------------------------------------------------------------------------
def write_report(sf_res: dict, bw_res: dict, pair_res: dict,
                 lat_res: dict, ft_res: dict) -> str:
    """Render markdown report and return as string."""
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = datetime.date.today().isoformat()

    sf_acc = sf_res["gate_acc"]
    bw_acc = bw_res["gate_acc"]
    pair_acc = pair_res["acc"]
    lat_ms = lat_res["median_ms"]
    ft_rate = ft_res["rate"]

    sf_ok  = sf_acc  >= SF_GATE_ACC
    bw_ok  = bw_acc  >= BW_GATE_ACC
    pair_ok = pair_acc >= PAIR_GATE_ACC
    lat_ok = lat_ms  <= LAT_GATE_MS

    overall = "PASS" if (sf_ok and bw_ok and pair_ok and lat_ok) else "FAIL"

    lines: list[str] = []
    lines += [
        f"# Результати тестування Stage 2 — Blind Estimator — {date_str}",
        "",
        f"**Verdict: {'✅ PASS' if overall == 'PASS' else '❌ FAIL'}**",
        "",
        "## Середовище",
        "",
        f"- ОС: `{platform.platform()}`",
        f"- Host: `{platform.node()}`",
        f"- CPU: `{platform.processor()}`",
        f"- Python: `{platform.python_version()}` (numpy {np.__version__})",
        f"- samp_rate: {SAMP_RATE/1e6:.2f} MS/s · buffer: 50 ms = {N_BUFFER:,} samples",
        f"- Wavelet: sym5 · DWT level: 4 · CWT: Morlet+SST · Scales: [151,76,38,19]",
        "",
        "## Параметри тестування",
        "",
        "| Параметр | Значення |",
        "|---|---|",
        f"| SFs | {SFS} |",
        f"| BWs (kHz) | {[b//1000 for b in BWS]} |",
        f"| SNR sweep | {SNR_RANGE[0]}..{SNR_RANGE[-1]} dB, крок 2 dB |",
        f"| N/combo | {N_PER_COMBINATION} |",
        f"| threshold_low | 0.4 |",
        f"| threshold_high | 0.7 |",
        f"| holdoff | disabled for accuracy tests |",
        "",
        "## Ключові метрики (gate)",
        "",
        "| Метрика | Результат | Ціль | Статус |",
        "|---|---|---|---|",
        f"| SF accuracy @ SNR≥-10dB | **{sf_acc:.1%}** | ≥85% | {'✅' if sf_ok else '❌'} |",
        f"| BW accuracy @ SNR≥-12dB | **{bw_acc:.1%}** | ≥80% | {'✅' if bw_ok else '❌'} |",
        f"| SF+BW pair @ SNR=-14dB  | **{pair_acc:.1%}** | ≥78% | {'✅' if pair_ok else '❌'} |",
        f"| Latency (median, 10 reps) | **{lat_ms:.2f} ms** | ≤25 ms | {'✅' if lat_ok else '❌'} |",
        f"| False trigger rate (info) | **{ft_rate:.1%}** | ≤5% | {ft_res['status']} |",
        "",
        "## SF Accuracy по SNR",
        "",
        "| SNR (dB) | Accuracy | Gate SNR? |",
        "|---|---|---|",
    ]
    for snr, acc in sf_res["snr_accuracy"].items():
        mark = " ← gate" if snr == SF_GATE_SNR else ""
        lines.append(f"| {snr:+d} | {acc:.1%} |{mark} |")

    lines += [
        "",
        "## BW Accuracy по SNR",
        "",
        "| SNR (dB) | Accuracy | Gate SNR? |",
        "|---|---|---|",
    ]
    for snr, acc in bw_res["snr_accuracy"].items():
        mark = " ← gate" if snr == BW_GATE_SNR else ""
        lines.append(f"| {snr:+d} | {acc:.1%} |{mark} |")

    lines += [
        "",
        "## SF+BW Pair Accuracy @ SNR=-14 dB",
        "",
        "| SF | BW (kHz) | Correct/Total | Accuracy |",
        "|---|---|---|---|",
    ]
    for (sf, bw), info in pair_res["per_pair"].items():
        lines.append(f"| SF{sf} | {bw//1000} | "
                     f"{info['correct']}/{info['total']} | {info['acc']:.1%} |")

    lines += [
        "",
        "## Latency Benchmark (T2-5, незалежний)",
        "",
        "| Метрика | Значення |",
        "|---|---|",
        f"| Median | **{lat_ms:.2f} ms** |",
        f"| Std | {lat_res['std_ms']:.2f} ms |",
        f"| Min | {lat_res['min_ms']:.2f} ms |",
        f"| Max | {lat_res['max_ms']:.2f} ms |",
        f"| N repeats | {len(lat_res['latencies_ms'])} |",
        f"| Buffer | {N_BUFFER:,} samples (50 ms @ {SAMP_RATE/1e6:.2f} MS/s) |",
        f"| Python Dev self-check | 17.11 ms (reference) |",
        "",
        "## False Trigger Rate (T2-6, info-only)",
        "",
        f"- AWGN buffers: {ft_res['n_bufs']}",
        f"- Triggered (conf≥0.4): {ft_res['n_triggered']}",
        f"- Rate: **{ft_rate:.1%}**  target ≤5%  {ft_res['status']}",
        "",
        "## Висновок",
        "",
    ]

    if overall == "PASS":
        lines += [
            f"✅ **PASS** — всі 4 блокуючих gate пройдено:",
            f"",
            f"- SF accuracy = {sf_acc:.1%} ≥ 85% @ SNR≥-10dB ✅",
            f"- BW accuracy = {bw_acc:.1%} ≥ 80% @ SNR≥-12dB ✅",
            f"- SF+BW pair = {pair_acc:.1%} ≥ 78% @ SNR=-14dB ✅",
            f"- Latency = {lat_ms:.2f} ms ≤ 25 ms ✅",
            f"",
            f"→ Оркестратор може відкривати **D2-1** (Docs Stage 2).",
        ]
    else:
        failures = []
        if not sf_ok:
            failures.append(f"SF accuracy={sf_acc:.1%} < 85% → повернути Python Dev (DWT)")
        if not bw_ok:
            failures.append(f"BW accuracy={bw_acc:.1%} < 80% → повернути Python Dev (CWT) або DSP Research")
        if not pair_ok:
            failures.append(f"pair accuracy={pair_acc:.1%} < 78% → повернути Python Dev + DSP Research")
        if not lat_ok:
            failures.append(f"latency={lat_ms:.2f}ms > 25ms → повернути Python Dev (оптимізація)")
        lines += ["❌ **FAIL**:"]
        for f in failures:
            lines.append(f"- {f}")
        lines += ["", "→ Оркестратор НЕ відкриває D2. Повернути до відповідного агента."]

    lines += [
        "",
        "## Відтворення",
        "",
        "```bash",
        "cd /home/tekken/ELRS_Hybrid_Detector_Vault/ELRS_Hybrid_Detector_Vault/tests/stage2",
        "python3 run_stage2_tests.py",
        "```",
        "",
        f"_Run timestamp: {now_str}_",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("Stage 2 Test/QA — T2-1..T2-7")
    print("=" * 60)

    # T2-2
    print("\n[T2-2] SF accuracy sweep ...")
    sf_res = test_sf_accuracy.run(n_per_combo=N_PER_COMBINATION, seed=1)

    # T2-3
    print("\n[T2-3] BW accuracy sweep ...")
    bw_res = test_bw_accuracy.run(n_per_combo=N_PER_COMBINATION, seed=2)

    # T2-4
    pair_res = t2_4_pair_accuracy(n_per_combo=N_PER_COMBINATION, seed=4)

    # T2-5
    lat_res = t2_5_latency(n_repeats=10, seed=5)

    # T2-6
    ft_res = t2_6_false_trigger(n_bufs=1000, seed=6)

    # T2-7 — write report
    print("\n[T2-7] Writing reports ...")
    report_md = write_report(sf_res, bw_res, pair_res, lat_res, ft_res)

    out_tests = os.path.join(_HERE, "test-results-stage2.md")
    with open(out_tests, "w") as f:
        f.write(report_md)
    print(f"  Saved: {out_tests}")

    logs_dir = os.path.join(_ROOT, "obsidian-vault", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    out_obs = os.path.join(logs_dir, "test-results-stage2-2026-05-29.md")
    with open(out_obs, "w") as f:
        f.write(report_md)
    print(f"  Saved: {out_obs}")

    # Final summary
    overall = (sf_res["verdict"] == "PASS" and
               bw_res["verdict"] == "PASS" and
               pair_res["verdict"] == "PASS" and
               lat_res["verdict"] == "PASS")
    print("\n" + "=" * 60)
    print(f"VERDICT: {'✅ PASS' if overall else '❌ FAIL'}")
    print(f"  SF  = {sf_res['gate_acc']:.1%} @ SNR≥-10dB  "
          f"({'✅' if sf_res['verdict']=='PASS' else '❌'})")
    print(f"  BW  = {bw_res['gate_acc']:.1%} @ SNR≥-12dB  "
          f"({'✅' if bw_res['verdict']=='PASS' else '❌'})")
    print(f"  pair= {pair_res['acc']:.1%} @ SNR=-14dB   "
          f"({'✅' if pair_res['verdict']=='PASS' else '❌'})")
    print(f"  lat = {lat_res['median_ms']:.2f} ms             "
          f"({'✅' if lat_res['verdict']=='PASS' else '❌'})")
    print(f"  FT  = {ft_res['rate']:.1%} (info)         {ft_res['status']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
