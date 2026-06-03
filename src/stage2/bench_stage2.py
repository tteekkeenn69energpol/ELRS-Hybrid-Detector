"""Stage 2 latency benchmark — C2-6.

Generates a synthetic complex64 buffer of 50 ms at 30.72 MS/s and measures
the median latency of ELRS_BlindParameterEstimator.estimate() over 10 runs.
Target: ≤ 25 ms median on RTX 3070.
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np

# Resolve sibling imports when run directly.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from blind_estimator import ELRS_BlindParameterEstimator

# -----------------------------------------------------------------------
# Constants — all parameterised, no magic numbers in logic below.
# -----------------------------------------------------------------------
SAMP_RATE: float = 30.72e6
BUFFER_MS: float = 50.0
N_REPEATS: int = 10
TARGET_MS: float = 25.0

N_SAMPLES: int = round(SAMP_RATE * BUFFER_MS / 1000.0)  # 1_536_000


def _make_synthetic_buffer(n: int, rng: np.random.Generator) -> np.ndarray:
    """Return a complex64 AWGN buffer of *n* samples."""
    real = rng.standard_normal(n).astype(np.float32)
    imag = rng.standard_normal(n).astype(np.float32)
    return (real + 1j * imag).astype(np.complex64)


def main() -> None:
    rng = np.random.default_rng(seed=42)
    buf = _make_synthetic_buffer(N_SAMPLES, rng)

    estimator = ELRS_BlindParameterEstimator(
        samp_rate=SAMP_RATE,
        wavelet="sym5",
        dwt_level=4,
        threshold_low=0.4,
        threshold_high=0.7,
        use_sst=True,
        dwt_score_bounds=(1.0, 10.0),
        cwt_energy_bounds=(1.0, 10.0),
        holdoff_s=0.0,  # disable holdoff so all 10 runs execute
    )

    latencies_ms: list[float] = []

    for _ in range(N_REPEATS):
        t0 = time.perf_counter()
        estimator.estimate(buf)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)

    median_ms = float(np.median(latencies_ms))
    verdict = "PASS" if median_ms <= TARGET_MS else "FAIL"

    print(
        f"Latency: {median_ms:.2f} ms (median, n={N_REPEATS})"
        f" — target ≤ {TARGET_MS:.1f} ms — {verdict}"
    )
    print(f"  min={min(latencies_ms):.2f} ms  max={max(latencies_ms):.2f} ms")
    print(f"  buffer: {N_SAMPLES:,} samples ({BUFFER_MS:.0f} ms @ {SAMP_RATE/1e6:.2f} MS/s)")


if __name__ == "__main__":
    main()
