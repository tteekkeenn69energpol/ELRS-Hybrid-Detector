"""Welch PSD-based Bandwidth estimator (CPU, Stage 2 v5).

Replaces CWT/SST with Welch power spectral density estimation per spec §R2-2
approved-v5. Signature and return keys unchanged for R2-4 compatibility.
"""

from __future__ import annotations

import numpy as np
from scipy.fft import rfft as sp_rfft, rfftfreq as sp_rfftfreq

# cupy is optional; used only for GPU array transfer utilities.
try:
    import cupy as cp
    _HAS_CUPY = True
except ImportError:
    cp = None  # type: ignore[assignment]
    _HAS_CUPY = False


_TARGET_BWS: list[int] = [203_000, 406_000, 812_000, 1_625_000]

# Welch PSD parameters (spec §R2-2 approved-v5, hardcoded)
_N_TOTAL: int = 65_536        # 2.13 ms @ 30.72 MS/s; K=31 frames
_N_FFT: int = 4_096           # bin_width = 7.5 kHz; resolution ≈ 4% of BW_min
_HOP: int = 2_048             # 50% overlap → K = (65536-4096)/2048+1 = 31
_NOISE_FREQ_MIN: float = 3_250_000.0   # > 2×max(target_bws); clean noise region


def cwt_bw_estimation(
    iq: "np.ndarray | cp.ndarray",
    samp_rate: float = 30.72e6,
    use_sst: bool = True,
    target_bws: list[int] | None = None,
    cwt_max_samples: int = 8_192,
    t_offset: int = 0,
) -> dict:
    """Estimate Bandwidth from an IQ buffer using Welch PSD (v5).

    use_sst and cwt_max_samples are retained for API compatibility (R2-4)
    but are not used in v5; Welch PSD replaces the CWT/SST pipeline.

    Parameters
    ----------
    iq : np.ndarray or cp.ndarray, dtype complex64
        Raw IQ samples at *samp_rate*.  Minimum length: _N_TOTAL = 65,536.
    samp_rate : float
        Sample rate in Hz.
    use_sst : bool
        Retained for API compatibility; not used in v5.
    target_bws : list[int] | None
        BW candidates in Hz; defaults to [203k, 406k, 812k, 1625k].
    cwt_max_samples : int
        Retained for API compatibility; not used in v5.

    Returns
    -------
    dict
        'bw'          : int   — estimated BW in Hz (one of target_bws)
        'energy'      : float — mean in-band normalised PSD power
        'energy_ratio': float — in-band / out-band power ratio ≥ 1.0
        'sst_used'    : bool  — always False in v5
    """
    if target_bws is None:
        target_bws = _TARGET_BWS

    # Ensure NumPy on CPU (CuPy → NumPy transfer, unchanged from v4)
    if _HAS_CUPY and isinstance(iq, cp.ndarray):
        iq_np: np.ndarray = cp.asnumpy(iq)
    else:
        iq_np = np.asarray(iq)

    # Step 1: prepare signal — Re(IQ), first N_TOTAL samples
    signal = np.real(iq_np[t_offset : t_offset + _N_TOTAL]).astype(np.float64)

    # Step 2: Welch PSD — K Hann-windowed frames, 50% overlap
    hann_win = np.hanning(_N_FFT)
    S_welch = np.zeros(_N_FFT // 2 + 1, dtype=np.float64)
    K = 0
    start = 0
    while start + _N_FFT <= len(signal):
        frame = signal[start:start + _N_FFT] * hann_win
        S_welch += np.abs(sp_rfft(frame, n=_N_FFT)) ** 2
        K += 1
        start += _HOP
    if K == 0:
        K = 1  # guard: avoid division by zero for very short signals
    S_welch /= K

    # Step 3: normalised PSD — noise floor = median(S[freqs > noise_freq_min])
    freqs = sp_rfftfreq(_N_FFT, d=1.0 / samp_rate)
    noise_mask = freqs > _NOISE_FREQ_MIN
    noise_vals = S_welch[noise_mask]
    noise_floor = float(np.median(noise_vals)) if len(noise_vals) > 0 else 1e-30
    noise_floor = max(noise_floor, 1e-30)
    S_norm = S_welch / noise_floor

    # Step 4: per-class hypothesis test — immune to noise outliers, no threshold needed
    # Physics: for true BW=b → ref_mask[b/2..b] is noise → ref_mean≈1.0 → score = 1 + SNR_spectral
    #          for wrong BW<b → ref_mask is inside signal band → ref_mean≈in_mean → score≈1.0
    scores = {}
    for b in target_bws:
        in_mask  = (freqs > 0) & (freqs <= b / 2.0)
        ref_mask = (freqs > b / 2.0) & (freqs <= float(b))
        in_mean  = float(np.mean(S_norm[in_mask]))  if np.any(in_mask)  else 1.0
        ref_mean = float(np.mean(S_norm[ref_mask])) if np.any(ref_mask) else 1.0
        ref_mean = max(ref_mean, 1e-6)
        scores[b] = in_mean / ref_mean

    # Step 5: select BW class with highest in/ref ratio
    bw_candidate = max(scores, key=scores.get)

    # Step 6: energy ratio — reuse score; compatible with cwt_energy_bounds=(1.0, 10.0)
    energy_ratio = max(scores[bw_candidate], 1.0)
    in_mask_best = (freqs > 0) & (freqs <= bw_candidate / 2.0)
    best_energy = float(np.mean(S_norm[in_mask_best])) if np.any(in_mask_best) else 1.0

    return {
        "bw": bw_candidate,
        "energy": best_energy,
        "energy_ratio": energy_ratio,
        "sst_used": False,
    }
