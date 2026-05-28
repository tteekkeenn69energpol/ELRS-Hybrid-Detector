"""ctypes binding for /tests/libcfar2d_c.so → CFAR2D from /src/.

Read-only consumer. Used by the Test/QA suite (Pfa MC, ROC, throughput).
"""

import ctypes
import os
from dataclasses import dataclass

import numpy as np

_LIB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libcfar2d_c.so")
_lib = ctypes.CDLL(_LIB_PATH)


class _DetectionC(ctypes.Structure):
    _fields_ = [
        ("t_idx",    ctypes.c_int32),
        ("f_idx",    ctypes.c_int32),
        ("power_db", ctypes.c_float),
        ("snr_db",   ctypes.c_float),
    ]


_lib.cfar2d_create.restype  = ctypes.c_void_p
_lib.cfar2d_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                               ctypes.c_float, ctypes.c_float, ctypes.c_float]

_lib.cfar2d_destroy.restype  = None
_lib.cfar2d_destroy.argtypes = [ctypes.c_void_p]

_lib.cfar2d_set_params.restype  = None
_lib.cfar2d_set_params.argtypes = [ctypes.c_void_p,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_float, ctypes.c_float, ctypes.c_float]

_lib.cfar2d_process.restype  = ctypes.c_int32
_lib.cfar2d_process.argtypes = [ctypes.c_void_p,
                                ctypes.POINTER(ctypes.c_float),
                                ctypes.c_int, ctypes.c_int,
                                ctypes.POINTER(_DetectionC), ctypes.c_int32,
                                ctypes.POINTER(ctypes.c_double)]

_lib.cfar2d_process_parallel.restype  = ctypes.c_int32
_lib.cfar2d_process_parallel.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                         ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                         ctypes.POINTER(ctypes.c_float),
                                         ctypes.c_int, ctypes.c_int,
                                         ctypes.c_int,
                                         ctypes.POINTER(_DetectionC), ctypes.c_int32,
                                         ctypes.POINTER(ctypes.c_double)]


@dataclass
class CFAR2DParams:
    N_ref_f: int = 16
    N_ref_t: int = 8
    N_guard_f: int = 4
    N_guard_t: int = 2
    rank_percent: float = 0.75
    threshold_db: float = 12.5
    min_snr_db: float = 7.0

    @property
    def N_train_total(self) -> int:
        outer_f = 2 * self.N_ref_f + 2 * self.N_guard_f + 1
        outer_t = 2 * self.N_ref_t + 2 * self.N_guard_t + 1
        guard_f = 2 * self.N_guard_f + 1
        guard_t = 2 * self.N_guard_t + 1
        return outer_f * outer_t - guard_f * guard_t

    @property
    def k(self) -> int:
        return int(round(self.rank_percent * self.N_train_total))

    @property
    def alpha_lin(self) -> float:
        return 10.0 ** (self.threshold_db / 10.0)


@dataclass
class Detection:
    t_idx: int
    f_idx: int
    power_db: float
    snr_db: float


class CFAR2D:
    """Stateful (single-thread) handle to the C++ CFAR2D class."""

    def __init__(self, params: CFAR2DParams = None):
        if params is None:
            params = CFAR2DParams()
        self.params = params
        self._handle = _lib.cfar2d_create(params.N_ref_f, params.N_ref_t,
                                          params.N_guard_f, params.N_guard_t,
                                          params.rank_percent, params.threshold_db,
                                          params.min_snr_db)
        self._buf_cap = 65536
        self._buf = (_DetectionC * self._buf_cap)()
        self._thrpt = ctypes.c_double(0.0)

    def __del__(self):
        if getattr(self, "_handle", None):
            _lib.cfar2d_destroy(self._handle)
            self._handle = None

    def set_params(self, p: CFAR2DParams):
        self.params = p
        _lib.cfar2d_set_params(self._handle, p.N_ref_f, p.N_ref_t,
                               p.N_guard_f, p.N_guard_t,
                               p.rank_percent, p.threshold_db, p.min_snr_db)

    def process(self, power: np.ndarray) -> tuple:
        """Returns (n_detections, throughput_ms, detections_list_first_N).

        n_detections is the total even if the buffer overflows; the returned
        list is truncated to the first _buf_cap entries.
        """
        if power.dtype != np.float32:
            raise TypeError("power must be float32")
        if not power.flags["C_CONTIGUOUS"]:
            power = np.ascontiguousarray(power)
        rows, cols = power.shape
        n = _lib.cfar2d_process(self._handle,
                                power.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                                rows, cols,
                                self._buf, self._buf_cap,
                                ctypes.byref(self._thrpt))
        ret = min(n, self._buf_cap)
        dets = [Detection(self._buf[i].t_idx, self._buf[i].f_idx,
                          self._buf[i].power_db, self._buf[i].snr_db)
                for i in range(ret)]
        return int(n), float(self._thrpt.value), dets


def process_parallel(power: np.ndarray, params: CFAR2DParams, nthreads: int):
    """One-shot parallel call: builds nthreads CFAR2D instances internally."""
    if power.dtype != np.float32:
        raise TypeError("power must be float32")
    if not power.flags["C_CONTIGUOUS"]:
        power = np.ascontiguousarray(power)
    rows, cols = power.shape
    cap = 65536
    buf = (_DetectionC * cap)()
    thrpt = ctypes.c_double(0.0)
    n = _lib.cfar2d_process_parallel(params.N_ref_f, params.N_ref_t,
                                     params.N_guard_f, params.N_guard_t,
                                     params.rank_percent, params.threshold_db,
                                     params.min_snr_db,
                                     power.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                                     rows, cols, nthreads,
                                     buf, cap,
                                     ctypes.byref(thrpt))
    ret = min(n, cap)
    dets = [Detection(buf[i].t_idx, buf[i].f_idx,
                      buf[i].power_db, buf[i].snr_db) for i in range(ret)]
    return int(n), float(thrpt.value), dets
