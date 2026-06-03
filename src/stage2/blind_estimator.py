"""Stage 2 — ELRS Blind Parameter Estimator (DWT + CWT + Confidence Gate)."""

from __future__ import annotations

import time
from collections import deque

import numpy as np

try:
    from .dwt_estimator import dwt_sf_estimation
    from .cwt_estimator import cwt_bw_estimation
except ImportError:
    from dwt_estimator import dwt_sf_estimation  # type: ignore[no-redef]
    from cwt_estimator import cwt_bw_estimation  # type: ignore[no-redef]


class ELRS_BlindParameterEstimator:
    """Blind SF/BW estimator for ELRS CSS signals (Stage 2).

    Pipeline (v3 CWT-first): Re(IQ[:8192]) → CWT(Morlet, scales=samp_rate/BW) [+SST] → BW
                             Re(IQ) → DWT(sym5, L=4, bw_hint) → autocorr → SF
                             → Confidence gate (0.4/0.7) → PDU dict

    Thread safety: one instance per thread (mutable internal state).
    """

    TARGET_BWS: list[int] = [203_000, 406_000, 812_000, 1_625_000]

    def __init__(
        self,
        samp_rate: float = 30.72e6,
        wavelet: str = "sym5",
        dwt_level: int = 4,
        threshold_low: float = 0.4,
        threshold_high: float = 0.7,
        use_sst: bool = True,
        dwt_score_bounds: tuple[float, float] = (1.0, 10.0),
        cwt_energy_bounds: tuple[float, float] = (1.0, 10.0),
        holdoff_s: float = 0.1,
    ) -> None:
        """
        samp_rate        — sample rate Hz (default: 30.72 MS/s SPECTRAN V6)
        wavelet          — PyWavelets name; 'sym5' (default) or 'sym8' (fallback)
        dwt_level        — decomposition level; 4 for 30.72 MS/s / 1625 kHz
        threshold_low    — confidence below this → REJECT
        threshold_high   — confidence at or above this → Stage 3 direct
        use_sst          — True: ssq_cwt (first-order SST); False: plain CWT
        dwt_score_bounds — (low, high) for normalizing DWT_score_raw → [0, 1]
        cwt_energy_bounds— (low, high) for normalizing CWT_energy_ratio → [0, 1]
        holdoff_s        — seconds to ignore triggers after a successful estimate
        """
        self._samp_rate = samp_rate
        self._wavelet = wavelet
        self._dwt_level = dwt_level
        self._threshold_low = threshold_low
        self._threshold_high = threshold_high
        self._use_sst = use_sst
        self._dwt_lo, self._dwt_hi = dwt_score_bounds
        self._cwt_lo, self._cwt_hi = cwt_energy_bounds
        self._holdoff_s = holdoff_s

        self._last_trigger_time: float = 0.0
        self._sf_history: deque[int] = deque(maxlen=10)

        # Warm up ssqueezepy JIT (numba) so first real estimate() is not penalised.
        self._warmup()

    # ------------------------------------------------------------------
    # Warmup
    # ------------------------------------------------------------------

    def _warmup(self) -> None:
        """Trigger ssqueezepy/numba JIT compilation with a tiny dummy buffer."""
        import numpy as _np
        dummy = (_np.zeros(256, dtype=_np.complex64) + 1.0)
        # Suppress warmup from affecting trigger state
        _saved = self._last_trigger_time
        try:
            cwt_bw_estimation(dummy, samp_rate=self._samp_rate, use_sst=self._use_sst)
        except Exception:
            pass  # warmup may fail for tiny dummy buffers; real calls use full-length IQ
        self._last_trigger_time = _saved

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def estimate(self, iq_buffer: np.ndarray, t_offset: int = 0) -> dict:
        """Estimate SF and BW from a complex64 IQ buffer.

        Parameters
        ----------
        iq_buffer : np.ndarray, dtype=complex64
            Raw IQ samples at self._samp_rate.
            Recommended length: 50–100 ms × samp_rate samples.

        Returns
        -------
        dict with keys:
            'sf'               : int
            'bw'               : int   (Hz)
            'confidence'       : float [0.0, 1.0]
            'method'           : str
            't_offset_samples' : int
            'stage3_ready'     : bool
            'needs_neural'     : bool
        """
        now = time.time()

        # --- Anti-false-trigger #1: holdoff ---
        if now - self._last_trigger_time < self._holdoff_s:
            return self._reject_result(0, self.TARGET_BWS[0], 0.0)

        # --- Anti-false-trigger #4: minimum buffer duration ---
        n = len(iq_buffer)
        # Use tightest constraint: SF7 @ BW=1625k → shortest symbol
        min_samples = int(0.5 * 8 * (2 ** 7) / 1_625_000 * self._samp_rate)
        if n < min_samples:
            return self._reject_result(0, self.TARGET_BWS[0], 0.0)

        # --- 2a: CWT BW estimator (first) ---
        cwt_result = cwt_bw_estimation(
            iq_buffer,
            samp_rate=self._samp_rate,
            use_sst=self._use_sst,
            target_bws=self.TARGET_BWS,
            t_offset=t_offset,
        )
        bw = cwt_result["bw"]
        cwt_energy_ratio = cwt_result["energy_ratio"]
        sst_used = cwt_result["sst_used"]

        # --- 2b: DWT SF estimator (bw_candidate from CWT) ---
        dwt_result = dwt_sf_estimation(
            iq_buffer,
            bw_candidate=bw,
            wavelet=self._wavelet,
            level=self._dwt_level,
            samp_rate=self._samp_rate,
            t_offset=t_offset,
        )
        sf = dwt_result["sf"]
        dwt_score_raw = dwt_result["score"]
        t_offset = dwt_result["t_offset_samples"]

        # --- 2c: Confidence gate ---
        dwt_norm = float(np.clip(
            (dwt_score_raw - self._dwt_lo) / max(self._dwt_hi - self._dwt_lo, 1e-9),
            0.0, 1.0,
        ))
        cwt_norm = float(np.clip(
            (cwt_energy_ratio - self._cwt_lo) / max(self._cwt_hi - self._cwt_lo, 1e-9),
            0.0, 1.0,
        ))
        confidence = 0.5 * dwt_norm + 0.5 * cwt_norm

        # --- Anti-false-trigger #3: SF history consistency ---
        if len(self._sf_history) >= 3:
            if float(np.std(list(self._sf_history)[-3:])) > 1.5:
                confidence *= 0.5

        # --- Anti-false-trigger #2: chirp rate consistency ---
        # We do not have measured_chirp_rate without a full phase analysis;
        # this placeholder activates only if bw/sf gives a clearly invalid rate.
        expected_chirp_rate = bw / (2 ** sf)  # Hz/s
        if expected_chirp_rate <= 0:
            confidence *= 0.3

        method = "psd+dwt"

        if confidence < self._threshold_low:
            return self._reject_result(sf, bw, confidence, method, t_offset)

        # Accept → update state
        self._last_trigger_time = now
        self._sf_history.append(sf)

        stage3_ready = confidence >= self._threshold_high
        needs_neural = not stage3_ready

        return {
            "sf": sf,
            "bw": bw,
            "confidence": confidence,
            "method": method,
            "t_offset_samples": t_offset,
            "stage3_ready": stage3_ready,
            "needs_neural": needs_neural,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _reject_result(
        sf: int,
        bw: int,
        confidence: float,
        method: str = "dwt+cwt",
        t_offset: int = 0,
    ) -> dict:
        return {
            "sf": sf,
            "bw": bw,
            "confidence": confidence,
            "method": method,
            "t_offset_samples": t_offset,
            "stage3_ready": False,
            "needs_neural": False,
        }
