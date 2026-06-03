"""T2-2 — SF accuracy test (BLOCKING gate: ≥85% @ SNR ≥ -10 dB).

Outputs:
  tests/stage2/sf_confusion_matrix.png   — confusion matrix heatmap
  Prints per-SNR accuracy table to stdout; returns to caller via run().
"""

from __future__ import annotations

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Make src/stage2 importable
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_TESTS_DIR, "..", "..", "src", "stage2")
sys.path.insert(0, _SRC_DIR)
sys.path.insert(0, _TESTS_DIR)

from blind_estimator import ELRS_BlindParameterEstimator
from synth_dataset import (
    make_iq_buffer, SFS, BWS, SNR_RANGE, N_PER_COMBINATION,
    SAMP_RATE, N_BUFFER,
)

SF_GATE_SNR: int = -10   # dB — gate applies at SNR ≥ this
SF_GATE_ACC: float = 0.85


def run(n_per_combo: int = N_PER_COMBINATION, seed: int = 1) -> dict:
    """Run SF accuracy sweep. Returns dict with per-SNR accuracy and verdict."""
    rng = np.random.default_rng(seed)

    est = ELRS_BlindParameterEstimator(
        samp_rate=SAMP_RATE,
        wavelet="sym5",
        dwt_level=4,
        threshold_low=0.0,   # disable gate so every buffer gets an SF estimate
        threshold_high=1.1,
        use_sst=True,
        holdoff_s=0.0,       # disable holdoff
    )

    sf_idx = {sf: i for i, sf in enumerate(SFS)}  # 7→0, 8→1, ..., 12→5

    # confusion[snr_idx][true_sf_idx][pred_sf_idx]
    n_snr = len(SNR_RANGE)
    n_sf = len(SFS)
    confusion = np.zeros((n_snr, n_sf, n_sf), dtype=np.int32)

    total_per_snr = n_sf * len(BWS) * n_per_combo

    print(f"T2-2 SF accuracy: {len(SFS)} SFs × {len(BWS)} BWs × "
          f"{n_per_combo} sigs × {n_snr} SNRs = "
          f"{n_sf * len(BWS) * n_per_combo * n_snr:,} estimates")

    for si, snr in enumerate(SNR_RANGE):
        for sf in SFS:
            for bw in BWS:
                for _ in range(n_per_combo):
                    buf = make_iq_buffer(sf, bw, snr_db=snr, rng=rng)
                    res = est.estimate(buf)
                    pred_sf = res["sf"]
                    confusion[si, sf_idx[sf], sf_idx.get(pred_sf, 0)] += 1

        correct = sum(confusion[si, i, i] for i in range(n_sf))
        acc = correct / total_per_snr
        print(f"  SNR={snr:+4d} dB  acc={acc:.3f}  ({correct}/{total_per_snr})")

    # Per-SNR accuracy
    snr_accuracy: dict[int, float] = {}
    for si, snr in enumerate(SNR_RANGE):
        correct = sum(confusion[si, i, i] for i in range(n_sf))
        snr_accuracy[snr] = correct / total_per_snr

    # Gate: worst accuracy at SNR ≥ gate
    gate_snrs = [s for s in SNR_RANGE if s >= SF_GATE_SNR]
    gate_acc = min(snr_accuracy[s] for s in gate_snrs)
    verdict = "PASS" if gate_acc >= SF_GATE_ACC else "FAIL"

    # Aggregate confusion matrix over all gate SNRs
    gate_indices = [SNR_RANGE.index(s) for s in gate_snrs]
    conf_gate = confusion[gate_indices].sum(axis=0)

    _plot(conf_gate, snr_accuracy, _TESTS_DIR)

    print(f"\nSF gate: min accuracy @ SNR≥{SF_GATE_SNR}dB = {gate_acc:.1%}  "
          f"(target ≥{SF_GATE_ACC:.0%})  → {verdict}")

    return {
        "snr_accuracy": snr_accuracy,
        "gate_acc": gate_acc,
        "verdict": verdict,
        "confusion_gate": conf_gate.tolist(),
    }


def _plot(conf_gate: np.ndarray, snr_accuracy: dict, out_dir: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: confusion matrix
    ax = axes[0]
    im = ax.imshow(conf_gate, cmap="Blues")
    ax.set_xticks(range(len(SFS))); ax.set_xticklabels([f"SF{s}" for s in SFS])
    ax.set_yticks(range(len(SFS))); ax.set_yticklabels([f"SF{s}" for s in SFS])
    ax.set_xlabel("Predicted SF"); ax.set_ylabel("True SF")
    ax.set_title("SF Confusion Matrix (SNR ≥ −10 dB, aggregated)")
    for i in range(len(SFS)):
        for j in range(len(SFS)):
            ax.text(j, i, str(conf_gate[i, j]),
                    ha="center", va="center", fontsize=8,
                    color="white" if conf_gate[i, j] > conf_gate.max() * 0.6 else "black")
    plt.colorbar(im, ax=ax)

    # Right: accuracy vs SNR
    ax2 = axes[1]
    snrs = list(snr_accuracy.keys())
    accs = [snr_accuracy[s] for s in snrs]
    ax2.plot(snrs, [a * 100 for a in accs], "o-", color="steelblue", label="SF accuracy")
    ax2.axhline(85, color="red", linestyle="--", label="Gate 85%")
    ax2.axvline(SF_GATE_SNR, color="orange", linestyle=":", label=f"Gate SNR {SF_GATE_SNR} dB")
    ax2.set_xlabel("SNR (dB)"); ax2.set_ylabel("Accuracy (%)")
    ax2.set_title("SF Accuracy vs SNR")
    ax2.legend(); ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 105)

    plt.tight_layout()
    out_path = os.path.join(out_dir, "sf_confusion_matrix.png")
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"  Plot saved: {out_path}")


if __name__ == "__main__":
    result = run()
    sys.exit(0 if result["verdict"] == "PASS" else 1)
