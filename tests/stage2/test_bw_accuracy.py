"""T2-3 — BW accuracy test (BLOCKING gate: ≥80% @ SNR ≥ -12 dB).

Outputs:
  tests/stage2/bw_confusion_matrix.png   — confusion matrix heatmap
  Returns dict from run() for aggregation in master runner.
"""

from __future__ import annotations

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_TESTS_DIR, "..", "..", "src", "stage2")
sys.path.insert(0, _SRC_DIR)
sys.path.insert(0, _TESTS_DIR)

from blind_estimator import ELRS_BlindParameterEstimator
from synth_dataset import (
    make_iq_buffer, SFS, BWS, SNR_RANGE, N_PER_COMBINATION,
    SAMP_RATE,
)

BW_GATE_SNR: int = -12
BW_GATE_ACC: float = 0.80
BW_LABELS: list[str] = ["203k", "406k", "812k", "1625k"]


def run(n_per_combo: int = N_PER_COMBINATION, seed: int = 2) -> dict:
    rng = np.random.default_rng(seed)

    est = ELRS_BlindParameterEstimator(
        samp_rate=SAMP_RATE,
        wavelet="sym5",
        dwt_level=4,
        threshold_low=0.0,
        threshold_high=1.1,
        use_sst=True,
        holdoff_s=0.0,
    )

    bw_idx = {bw: i for i, bw in enumerate(BWS)}
    n_snr = len(SNR_RANGE)
    n_bw = len(BWS)
    confusion = np.zeros((n_snr, n_bw, n_bw), dtype=np.int32)

    total_per_snr = len(SFS) * n_bw * n_per_combo

    print(f"T2-3 BW accuracy: {len(SFS)} SFs × {n_bw} BWs × "
          f"{n_per_combo} sigs × {n_snr} SNRs = "
          f"{total_per_snr * n_snr:,} estimates")

    for si, snr in enumerate(SNR_RANGE):
        for sf in SFS:
            for bw in BWS:
                for _ in range(n_per_combo):
                    buf = make_iq_buffer(sf, bw, snr_db=snr, rng=rng)
                    res = est.estimate(buf)
                    pred_bw = res["bw"]
                    pred_idx = bw_idx.get(pred_bw, 0)
                    confusion[si, bw_idx[bw], pred_idx] += 1

        correct = sum(confusion[si, i, i] for i in range(n_bw))
        acc = correct / total_per_snr
        print(f"  SNR={snr:+4d} dB  acc={acc:.3f}  ({correct}/{total_per_snr})")

    snr_accuracy: dict[int, float] = {}
    for si, snr in enumerate(SNR_RANGE):
        correct = sum(confusion[si, i, i] for i in range(n_bw))
        snr_accuracy[snr] = correct / total_per_snr

    gate_snrs = [s for s in SNR_RANGE if s >= BW_GATE_SNR]
    gate_acc = min(snr_accuracy[s] for s in gate_snrs)
    verdict = "PASS" if gate_acc >= BW_GATE_ACC else "FAIL"

    gate_indices = [SNR_RANGE.index(s) for s in gate_snrs]
    conf_gate = confusion[gate_indices].sum(axis=0)

    _plot(conf_gate, snr_accuracy, _TESTS_DIR)

    print(f"\nBW gate: min accuracy @ SNR≥{BW_GATE_SNR}dB = {gate_acc:.1%}  "
          f"(target ≥{BW_GATE_ACC:.0%})  → {verdict}")

    return {
        "snr_accuracy": snr_accuracy,
        "gate_acc": gate_acc,
        "verdict": verdict,
        "confusion_gate": conf_gate.tolist(),
    }


def _plot(conf_gate: np.ndarray, snr_accuracy: dict, out_dir: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    im = ax.imshow(conf_gate, cmap="Greens")
    ax.set_xticks(range(len(BWS))); ax.set_xticklabels(BW_LABELS)
    ax.set_yticks(range(len(BWS))); ax.set_yticklabels(BW_LABELS)
    ax.set_xlabel("Predicted BW"); ax.set_ylabel("True BW")
    ax.set_title("BW Confusion Matrix (SNR ≥ −12 dB, aggregated)")
    for i in range(len(BWS)):
        for j in range(len(BWS)):
            ax.text(j, i, str(conf_gate[i, j]),
                    ha="center", va="center", fontsize=9,
                    color="white" if conf_gate[i, j] > conf_gate.max() * 0.6 else "black")
    plt.colorbar(im, ax=ax)

    ax2 = axes[1]
    snrs = list(snr_accuracy.keys())
    accs = [snr_accuracy[s] for s in snrs]
    ax2.plot(snrs, [a * 100 for a in accs], "s-", color="seagreen", label="BW accuracy")
    ax2.axhline(80, color="red", linestyle="--", label="Gate 80%")
    ax2.axvline(BW_GATE_SNR, color="orange", linestyle=":", label=f"Gate SNR {BW_GATE_SNR} dB")
    ax2.set_xlabel("SNR (dB)"); ax2.set_ylabel("Accuracy (%)")
    ax2.set_title("BW Accuracy vs SNR")
    ax2.legend(); ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 105)

    plt.tight_layout()
    out_path = os.path.join(out_dir, "bw_confusion_matrix.png")
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"  Plot saved: {out_path}")


if __name__ == "__main__":
    result = run()
    sys.exit(0 if result["verdict"] == "PASS" else 1)
