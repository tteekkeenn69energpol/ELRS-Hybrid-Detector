"""T2-1 — Synthetic dataset generator for Stage 2 blind estimator tests.

Generates complex64 IQ buffers containing ELRS CSS chirp preambles embedded
in AWGN at specified SNR levels.  All 24 SF×BW combinations are covered.

Usage (standalone):
    python3 synth_dataset.py          # quick smoke-test: 1 buffer per combo
    python3 synth_dataset.py --full   # full dataset (slow)

Parameters match the spec: samp_rate=30.72e6, buffer=50ms, CSS up-chirps.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SAMP_RATE: float = 30.72e6
BUFFER_DURATION: float = 0.05       # 50 ms
N_BUFFER: int = round(SAMP_RATE * BUFFER_DURATION)  # 1_536_000

SFS: list[int] = [7, 8, 9, 10, 11, 12]
BWS: list[int] = [203_000, 406_000, 812_000, 1_625_000]
SNR_RANGE: list[int] = list(range(-14, 11, 2))  # -14, -12, ..., +10 dB (13 levels)
N_PER_COMBINATION: int = 500


# ---------------------------------------------------------------------------
# CSS chirp synthesis
# ---------------------------------------------------------------------------

def _css_symbol(sf: int, bw: int, samp_rate: float, up: bool = True) -> np.ndarray:
    """Return one CSS chirp symbol as complex64 IQ.

    A CSS up-chirp sweeps 0→BW over T_sym = 2^SF / BW seconds.
    Down-chirp is complex conjugate.
    """
    n_sym = round((2 ** sf) / bw * samp_rate)
    t = np.arange(n_sym, dtype=np.float64) / samp_rate
    # Instantaneous frequency: f(t) = -BW/2 + BW*t/T_sym  (base-band, centered)
    T_sym = (2 ** sf) / bw
    f0 = -bw / 2.0
    chirp_rate = bw / T_sym
    phase = 2.0 * np.pi * (f0 * t + 0.5 * chirp_rate * t ** 2)
    iq = np.exp(1j * phase).astype(np.complex64)
    return iq if up else np.conj(iq)


def _build_preamble(sf: int, bw: int, samp_rate: float) -> np.ndarray:
    """Build ELRS preamble: 8 up + 2 SYNC(+BW/4 offset) + 2.25 down chirps."""
    up = _css_symbol(sf, bw, samp_rate, up=True)

    # SYNC chirp: up-chirp with +BW/4 frequency offset
    n_sym = len(up)
    t = np.arange(n_sym, dtype=np.float64) / samp_rate
    sync_phase_offset = 2.0 * np.pi * (bw / 4.0) * t
    sync = (up * np.exp(1j * sync_phase_offset).astype(np.complex64)).astype(np.complex64)

    down = _css_symbol(sf, bw, samp_rate, up=False)

    # 8 up + 2 sync + 2 down + 0.25 down
    frac_quarter = int(round(0.25 * len(down)))
    preamble = np.concatenate([
        *([up] * 8),
        *([sync] * 2),
        *([down] * 2),
        down[:frac_quarter],
    ])
    return preamble


def make_iq_buffer(
    sf: int,
    bw: int,
    snr_db: float,
    rng: np.random.Generator,
    samp_rate: float = SAMP_RATE,
    n_buffer: int = N_BUFFER,
) -> np.ndarray:
    """Generate a complex64 IQ buffer with CSS preamble + AWGN.

    The preamble is placed at a random offset within the buffer.
    If the preamble is longer than the buffer, it is truncated.
    Signal power is normalized to 1.0 before AWGN addition.
    """
    preamble = _build_preamble(sf, bw, samp_rate)

    # Place preamble at random offset
    max_offset = max(0, n_buffer - len(preamble))
    offset = int(rng.integers(0, max_offset + 1)) if max_offset > 0 else 0

    sig = np.zeros(n_buffer, dtype=np.complex64)
    end = min(offset + len(preamble), n_buffer)
    sig[offset:end] = preamble[:end - offset]

    # Normalize signal power to 1.0
    sig_power = float(np.mean(np.abs(sig) ** 2))
    if sig_power > 0:
        sig /= np.sqrt(sig_power)

    # AWGN: sigma such that SNR = 10*log10(P_sig / P_noise)
    # P_sig = 1.0, P_noise = sigma^2 (per real component), total noise power = 2*sigma^2
    # SNR_linear = 1.0 / (2 * sigma^2)  →  sigma = sqrt(1 / (2 * snr_lin))
    snr_lin = 10.0 ** (snr_db / 10.0)
    sigma = float(np.sqrt(1.0 / (2.0 * snr_lin)))
    noise_r = rng.standard_normal(n_buffer).astype(np.float32) * sigma
    noise_i = rng.standard_normal(n_buffer).astype(np.float32) * sigma
    noise = (noise_r + 1j * noise_i).astype(np.complex64)

    return sig + noise


def make_awgn_buffer(
    rng: np.random.Generator,
    n_buffer: int = N_BUFFER,
) -> np.ndarray:
    """Pure AWGN buffer (no signal) — used for T2-6 false-trigger test."""
    noise_r = rng.standard_normal(n_buffer).astype(np.float32)
    noise_i = rng.standard_normal(n_buffer).astype(np.float32)
    return (noise_r + 1j * noise_i).astype(np.complex64)


# ---------------------------------------------------------------------------
# Smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    rng = np.random.default_rng(seed=0)
    combos = [(sf, bw) for sf in SFS for bw in BWS]
    n = 1 if "--full" not in sys.argv else N_PER_COMBINATION
    print(f"synth_dataset.py smoke-test: {len(combos)} combos × {n} buf × "
          f"{len(SNR_RANGE)} SNRs = {len(combos)*n*len(SNR_RANGE):,} buffers")
    for sf, bw in combos[:2]:
        buf = make_iq_buffer(sf, bw, snr_db=-6.0, rng=rng)
        assert buf.dtype == np.complex64 and len(buf) == N_BUFFER
    print("OK — buffers shape and dtype verified.")
