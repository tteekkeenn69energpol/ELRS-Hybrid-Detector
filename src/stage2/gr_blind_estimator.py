"""GNU Radio sync_block wrapper for ELRS Stage 2 Blind Parameter Estimator."""

from __future__ import annotations

import sys
import os
import time
import threading

import numpy as np

# Allow importing sibling modules when this file is loaded as an epy_block.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pmt
import gnuradio.gr as gr

from blind_estimator import ELRS_BlindParameterEstimator


class Blind_Parameter_Estimator(gr.sync_block):
    """GNU Radio block wrapping ELRS_BlindParameterEstimator (Stage 2).

    Streams complex64 IQ samples continuously. When triggered by a PMT
    message from Stage 1 OS-CFAR on port 'trigger', accumulates a 50 ms
    window and runs the DWT+CWT estimator. Results are published as a PDU
    on port 'pdu'.

    Ports
    -----
    trigger (in, message) : PMT dict from Stage 1 (key 'offset' expected)
    pdu     (out, message): PMT dict {sf, bw, confidence, stage3_ready,
                            needs_neural, t_offset_samples, method}
    """

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
        window_ms: float = 50.0,
    ) -> None:
        gr.sync_block.__init__(
            self,
            name="Blind Parameter Estimator",
            in_sig=[np.complex64],
            out_sig=None,
        )

        self._samp_rate = samp_rate
        self._window_samples = int(samp_rate * window_ms / 1000.0)
        self._holdoff_s = holdoff_s

        self._estimator = ELRS_BlindParameterEstimator(
            samp_rate=samp_rate,
            wavelet=wavelet,
            dwt_level=dwt_level,
            threshold_low=threshold_low,
            threshold_high=threshold_high,
            use_sst=use_sst,
            dwt_score_bounds=dwt_score_bounds,
            cwt_energy_bounds=cwt_energy_bounds,
            holdoff_s=holdoff_s,
        )

        # Ring buffer — pre-allocated, no heap allocations in work()
        self._ring: np.ndarray = np.zeros(self._window_samples * 2, dtype=np.complex64)
        self._ring_pos: int = 0  # write head (circular)
        self._lock = threading.Lock()
        self._last_pub: float = 0.0

        self.message_port_register_in(pmt.intern("trigger"))
        self.message_port_register_out(pmt.intern("pdu"))
        self.set_msg_handler(pmt.intern("trigger"), self._handle_trigger)

    # ------------------------------------------------------------------
    # GNU Radio work
    # ------------------------------------------------------------------

    def work(self, input_items: list[np.ndarray], output_items: list) -> int:
        samples = input_items[0]
        n = len(samples)

        with self._lock:
            # Write into ring buffer (wrap-around)
            cap = len(self._ring)
            start = self._ring_pos % cap
            end = start + n
            if end <= cap:
                self._ring[start:end] = samples
            else:
                first = cap - start
                self._ring[start:] = samples[:first]
                self._ring[:n - first] = samples[first:]
            self._ring_pos += n

        return n

    # ------------------------------------------------------------------
    # PMT message handler (runs in GNU Radio message thread)
    # ------------------------------------------------------------------

    def _handle_trigger(self, msg: pmt.pmt_base) -> None:  # type: ignore[type-arg]
        """Process a trigger PMT from Stage 1; run estimator; publish PDU."""
        now = time.time()
        if now - self._last_pub < self._holdoff_s:
            return

        with self._lock:
            pos = self._ring_pos
            cap = len(self._ring)
            w = self._window_samples
            if pos < w:
                return  # not enough samples yet

            # Extract the most recent `w` samples from the ring
            end = pos % cap
            start = (pos - w) % cap
            if start < end:
                buf: np.ndarray = self._ring[start:end].copy()
            else:
                buf = np.concatenate([self._ring[start:], self._ring[:end]])

        result = self._estimator.estimate(buf)

        # Only publish on edge (new accepted estimate, not a reject)
        if not result["stage3_ready"] and not result["needs_neural"]:
            return

        self._last_pub = time.time()
        self._publish_pdu(result)

    def _publish_pdu(self, result: dict) -> None:
        meta = pmt.make_dict()
        meta = pmt.dict_add(meta, pmt.intern("sf"),          pmt.from_long(result["sf"]))
        meta = pmt.dict_add(meta, pmt.intern("bw"),          pmt.from_long(result["bw"]))
        meta = pmt.dict_add(meta, pmt.intern("confidence"),  pmt.from_double(result["confidence"]))
        meta = pmt.dict_add(meta, pmt.intern("stage3_ready"),pmt.from_bool(result["stage3_ready"]))
        meta = pmt.dict_add(meta, pmt.intern("needs_neural"),pmt.from_bool(result["needs_neural"]))
        meta = pmt.dict_add(meta, pmt.intern("t_offset"),    pmt.from_long(result["t_offset_samples"]))
        meta = pmt.dict_add(meta, pmt.intern("method"),      pmt.intern(result["method"]))

        # PDU = (meta_dict, empty_vector)
        pdu = pmt.cons(meta, pmt.make_u8vector(0, 0))
        self.message_port_pub(pmt.intern("pdu"), pdu)
