"""Synthetic-data generators for Test/QA.

Conforms to cfar-spec.md §85-86:
  fft_size = 2048, hop = fft_size/4 (75% overlap), window = Blackman-Harris,
  samp_rate = 30.72 MS/s, linear-power matrix on CFAR2D input.

ELRS-style chirp preamble (spec §75-77): 8 up-chirps + 2 SYNC + 2.25 down-chirps.
"""

import numpy as np


FS         = 30.72e6
FFT_SIZE   = 2048
HOP        = FFT_SIZE // 4   # 512  → 75% overlap
N_OVERLAP  = FFT_SIZE - HOP

# Blackman-Harris (4-term) window — precomputed once.
_BH_WIN = np.blackman(FFT_SIZE).astype(np.float32) if False else None
def _bh_window(N: int) -> np.ndarray:
    # 4-term Blackman-Harris (Harris 1978).
    n = np.arange(N)
    a0, a1, a2, a3 = 0.35875, 0.48829, 0.14128, 0.01168
    w = (a0
         - a1 * np.cos(2 * np.pi * n / (N - 1))
         + a2 * np.cos(4 * np.pi * n / (N - 1))
         - a3 * np.cos(6 * np.pi * n / (N - 1)))
    return w.astype(np.float32)

_WIN = _bh_window(FFT_SIZE)


# ---------------------------------------------------------------------------
# IQ generators
# ---------------------------------------------------------------------------
def awgn_iq(n_samples: int, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Complex AWGN, var(re)=var(im)=sigma^2/2 → total power = sigma^2."""
    a = rng.standard_normal(n_samples).astype(np.float32)
    b = rng.standard_normal(n_samples).astype(np.float32)
    iq = (a + 1j * b).astype(np.complex64) * np.float32(sigma / np.sqrt(2.0))
    return iq


def elrs_chirp_iq(n_samples: int, fs: float, amp: float,
                  t0_sample: int, rng: np.random.Generator,
                  sf: int = 7, bw: float = 500e3,
                  n_up: int = 8, n_sync: int = 2, n_down: float = 2.25,
                  freq_offset: float = 0.0) -> np.ndarray:
    """Generate an ELRS-style chirp preamble embedded in an n_samples vector.

    Returns a complex64 vector of length n_samples with the preamble placed
    starting at sample index t0_sample.  Outside the preamble the vector is
    zero (caller adds AWGN).

    Chirp model: CSS-style linear FM. T_chirp = 2^sf / bw.
      - 8 up-chirps   : f(t) = f0 + (bw/T)·t  for t in [0, T]
      - 2 SYNC chirps : up-chirps with the same slope but offset center freq
                        (LoRa convention; we use +bw/4 offset)
      - 2.25 down-chirps : f(t) = f0 - (bw/T)·t
                        (the trailing 0.25 is the SFD as in LoRa)
    The carrier is placed at a random offset within ±fs/4 to exercise CFAR
    across the spectrogram (not always centered).
    """
    T_chirp = (1 << sf) / bw
    n_per_chirp = int(round(T_chirp * fs))
    total_chirps = n_up + n_sync + n_down
    n_preamble = int(round(total_chirps * n_per_chirp))

    # Random carrier offset so the chirp doesn't always land in the same bins.
    f_carrier = (rng.uniform(-1.0, 1.0) * fs / 4.0) + freq_offset
    slope = bw / T_chirp

    # Build the chirp waveform.
    t_loc = np.arange(n_preamble, dtype=np.float64) / fs
    phase = np.zeros(n_preamble, dtype=np.float64)

    idx = 0
    # 8 up-chirps.
    for _ in range(n_up):
        tt = np.arange(n_per_chirp, dtype=np.float64) / fs
        # instantaneous freq sweeps from -bw/2 to +bw/2 around carrier
        f_inst = f_carrier - bw / 2.0 + slope * tt
        ph = 2.0 * np.pi * np.cumsum(f_inst) / fs
        phase[idx:idx + n_per_chirp] = ph
        idx += n_per_chirp
    # 2 SYNC (up-chirps offset by +bw/4).
    for _ in range(n_sync):
        tt = np.arange(n_per_chirp, dtype=np.float64) / fs
        f_inst = (f_carrier + bw / 4.0) - bw / 2.0 + slope * tt
        ph = 2.0 * np.pi * np.cumsum(f_inst) / fs
        phase[idx:idx + n_per_chirp] = ph
        idx += n_per_chirp
    # 2.25 down-chirps.
    n_down_full = int(n_down * n_per_chirp)
    tt = np.arange(n_down_full, dtype=np.float64) / fs
    f_inst = f_carrier + bw / 2.0 - slope * tt
    ph = 2.0 * np.pi * np.cumsum(f_inst) / fs
    phase[idx:idx + n_down_full] = ph
    idx += n_down_full

    waveform = (amp * np.exp(1j * phase[:idx])).astype(np.complex64)

    out = np.zeros(n_samples, dtype=np.complex64)
    end = min(t0_sample + idx, n_samples)
    out[t0_sample:end] = waveform[:end - t0_sample]
    return out, t0_sample, t0_sample + idx


# ---------------------------------------------------------------------------
# STFT → power matrix (linear, float32, row-major time×freq)
# ---------------------------------------------------------------------------
def stft_power(iq: np.ndarray) -> np.ndarray:
    """Row-major linear power |FFT|² matrix (rows=time frames, cols=freq bins).

    Window = Blackman-Harris, fftshift applied (DC at bin fft_size/2), per spec.
    """
    n = iq.size
    n_frames = max(0, (n - FFT_SIZE) // HOP + 1)
    if n_frames <= 0:
        return np.zeros((0, FFT_SIZE), dtype=np.float32)

    # Frame the signal: shape (n_frames, FFT_SIZE)
    stride = iq.strides[0]
    frames = np.lib.stride_tricks.as_strided(
        iq, shape=(n_frames, FFT_SIZE),
        strides=(HOP * stride, stride), writeable=False).copy()
    frames *= _WIN  # broadcast

    # FFT + shift + magnitude squared
    X = np.fft.fft(frames, axis=1)
    X = np.fft.fftshift(X, axes=1)
    P = (X.real * X.real + X.imag * X.imag).astype(np.float32)
    return P


def make_awgn_matrix(n_frames: int, sigma: float,
                     rng: np.random.Generator) -> np.ndarray:
    """One AWGN power-matrix of shape (n_frames, FFT_SIZE)."""
    n_iq = (n_frames - 1) * HOP + FFT_SIZE
    iq = awgn_iq(n_iq, sigma, rng)
    P = stft_power(iq)
    # stft_power may return slightly different n_frames; clip to n_frames
    if P.shape[0] >= n_frames:
        return np.ascontiguousarray(P[:n_frames])
    pad = np.zeros((n_frames - P.shape[0], FFT_SIZE), dtype=np.float32)
    return np.ascontiguousarray(np.concatenate([P, pad], axis=0))


def make_packet_matrix(n_frames: int, sigma: float, snr_db: float,
                       rng: np.random.Generator):
    """AWGN + ELRS chirp preamble. Returns (power_matrix, chirp_frame_range).

    chirp_frame_range = (frame_lo, frame_hi) — frames containing the preamble.
    Used by Pd estimation to gate detections to the preamble window.
    """
    n_iq = (n_frames - 1) * HOP + FFT_SIZE
    # Carrier-domain SNR in dB → chirp amplitude relative to noise σ.
    amp = np.float32(sigma * (10.0 ** (snr_db / 20.0)))

    # Place preamble so it lies fully inside the matrix with some margin.
    T_chirp = 128.0 / 500e3      # 2^7/500kHz = 256 µs
    n_per_chirp = int(round(T_chirp * FS))
    n_preamble = int(round(12.25 * n_per_chirp))
    margin_iq = HOP * 8           # ~8 frames of pad before & after
    t0_iq = max(margin_iq, rng.integers(margin_iq, max(margin_iq + 1, n_iq - n_preamble - margin_iq)))
    chirp, s0, s1 = elrs_chirp_iq(n_iq, FS, amp, int(t0_iq), rng)

    noise = awgn_iq(n_iq, sigma, rng)
    iq = (noise + chirp).astype(np.complex64)

    P = stft_power(iq)
    if P.shape[0] < n_frames:
        pad = np.zeros((n_frames - P.shape[0], FFT_SIZE), dtype=np.float32)
        P = np.concatenate([P, pad], axis=0)
    P = np.ascontiguousarray(P[:n_frames])

    # Frame index range covering the preamble.
    frame_lo = max(0, (s0 - FFT_SIZE) // HOP)
    frame_hi = min(n_frames - 1, s1 // HOP)
    return P, (int(frame_lo), int(frame_hi))
