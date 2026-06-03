"""Dechirp Matched Filter SF estimator (CPU, Stage 2 v7).

Replaces DWT autocorrelation per spec §R2-1 v7. Signature and return keys
unchanged for R2-4 compatibility. wavelet/level retained for API compat only.
"""

from __future__ import annotations

import numpy as np
from scipy.fft import fft as sp_fft


_SF_RANGE = range(7, 13)
_N_DECHIRP_MAX: int = 65_536   # v8: max FFT window; caps latency for SF12/203k


def dwt_sf_estimation(
    iq: np.ndarray,
    bw_candidate: int,
    wavelet: str = "sym5",
    level: int = 4,
    samp_rate: float = 30.72e6,
    t_offset: int = 0,
) -> dict:
    """Estimate Spreading Factor using Dechirp Matched Filter (v7).

    For each SF hypothesis in 7..12: multiply IQ by reference down-chirp,
    compute |rfft(dechirped, n=n_sym)|², score = peak / mean. argmax = SF.

    Parameters
    ----------
    iq : np.ndarray, dtype complex64
        Raw IQ samples at *samp_rate*.
    bw_candidate : int
        BW in Hz from the preceding Welch PSD step (§R2-2).
    wavelet : str
        Retained for API compatibility (R2-4); not used in v7.
    level : int
        Retained for API compatibility (R2-4); not used in v7.
    samp_rate : float
        Sample rate in Hz.

    Returns
    -------
    dict
        'sf'               : int   — best SF 7..12
        'bw_hint'          : int   — bw_candidate (pass-through)
        'score'            : float — peak/mean ratio (≥ 1.0)
        'best_lag'         : int   — always 0 in v7 (API compatibility)
        't_offset_samples' : int   — 10% cumulative energy point
    """
    iq_arr = np.asarray(iq, dtype=np.complex64)
    n_total = len(iq_arr)

    scores: dict[int, float] = {}

    for sf_hat in _SF_RANGE:
        n_sym = round((2 ** sf_hat) * samp_rate / bw_candidate)
        n_use = min(n_sym, _N_DECHIRP_MAX, n_total - t_offset)
        if n_use <= 0:
            scores[sf_hat] = 1.0
            continue

        t = np.arange(n_use, dtype=np.float64) / samp_rate
        f0 = -float(bw_candidate) / 2.0
        cr_hat = float(bw_candidate) ** 2 / float(2 ** sf_hat)

        ref_phase = 2.0 * np.pi * (f0 * t + 0.5 * cr_hat * t * t)
        ref = np.exp(-1j * ref_phase).astype(np.complex64)

        dechirped = iq_arr[t_offset : t_offset + n_use] * ref
        spectrum = np.abs(sp_fft(dechirped, n=n_use)) ** 2

        peak_val = float(np.max(spectrum))
        mean_val = max(float(np.mean(spectrum)), 1e-30)
        scores[sf_hat] = peak_val / mean_val

    best_sf = max(scores, key=scores.get)
    sf_score = float(scores[best_sf])

    # t_offset_samples: first index where cumsum(|iq|²) ≥ 0.1 × total energy
    energy_env = np.abs(iq_arr) ** 2
    total_e = float(np.sum(energy_env))
    if total_e > 0:
        cumulative_e = np.cumsum(energy_env)
        indices = np.where(cumulative_e >= 0.1 * total_e)[0]
        t_offset_samples = int(indices[0]) if len(indices) > 0 else 0
    else:
        t_offset_samples = 0

    return {
        "sf": best_sf,
        "bw_hint": bw_candidate,
        "score": sf_score,
        "best_lag": 0,
        "t_offset_samples": t_offset_samples,
    }
