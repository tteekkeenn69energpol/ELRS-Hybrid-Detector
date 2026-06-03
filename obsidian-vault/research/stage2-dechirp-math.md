---
tags: [stage-2, knowledge-builder, dechirp, orthogonality, cfo, sto, math]
created: 2026-05-29
type: analysis
stage: 3
status: done
drive_folder_id: 1YKR02MsWSyqnjr2D3bTtOO6IYHScgAsj
drive_doc_id: 1Ych1K251gjWpdZQQox8CF7ceKEPBwrS1jiLWFTLkxgc
source: "Документ без назви — dechirping math (Google Drive)"
---

# Математика Dechirping та Ортогональність LoRa CSS

Аналіз математичних основ dechirping, ортогональності символів, CFO/STO впливу та matched filter bank для Stage 3.

---

## 1. Ортогональність символів LoRa

Для SF: набір N = 2^SF можливих символів утворює **повний ортогональний базис** у N-вимірному комплексному просторі.

### Dechirping механізм
1. **Dechirping:** `y = x_received × conj(reference_upchirp)` → wideband sweep → constant-freq tone
2. **FFT:** energy концентрується у **єдиному спектральному піку** = символ index

### Quasi-ортогональність між різними SF
- Різні SF: quasi-orthogonal (різні frequency slopes)
- Dechirping fails для іншого SF → energy залишається розподіленою → "noise floor"

---

## 2. Вплив Phase Noise

| Тип | Вплив |
|-----|-------|
| Low-frequency drift (flicker) | Локальний frequency offset → пік зміщується в adjacent bins |
| High-frequency jitter | Peak broadening → spectral leakage → reduced Peak SNR |

---

## 3. Dechirp + FFT vs Time-Domain Matched Filter

### Обчислювальна ефективність

| Метод | Складність | Переваги |
|-------|-----------|----------|
| FFT Dechirp | **O(N log N)** | Всі N циклічних зсувів одночасно |
| Time-domain XCorr | O(N²) naively | Максимальна temporal resolution |
| GPU Fused Kernels | O(N log N) parallel | Сотні concurrent channels |

### SNR trade-off
- **Dechirp + FFT:** fractional CFO → spectral leakage (scalloping loss)
- **Time-domain:** менш чутливий до leakage, sub-microsecond ToA accuracy

### Коли що використовувати:
- **Dechirp + FFT:** symbol decoding (стандартний шлях)
- **Time-domain:** ranging, timestamping (< 1 мкс ToA)

---

## 4. Matched Filter Bank для SF/BW hypotheses

### Архітектура паралельного виконання

```
ADC → IQ baseband
         ↓ (копії)
  [SF7, BW203] correlator    [SF7, BW406] correlator  ...
  [SF8, BW203] correlator    ...                       ...
  ...
  [SF12, BW1625] correlator  (всього 6×4 = 24 parallel)
         ↓
   peak detection → best hypothesis → {sf, bw, cfo}
```

1. **Forward FFT** (received signal)
2. **Point-wise multiplication** (× conj(reference spectrum))
3. **IFFT** → correlation sequence → O(N log N)

### Dynamic Multi-Rate Scheduling
- **Pre-allocated cuFFT plans** для N ∈ {128, 256, ..., 4096}
- **Triggered execution:** CFAR trigger → запуск heavy MF
- **Decoupled sampling:** samp_rate = common multiple of all BW → integer N per chirp

---

## 5. CFO Tolerance Limits

### Математична межа: 0.5 bins
- Energy fails: > 0.5 bins residual CFO
- At 0.5 bins: energy split equally між двома adjacent bins → ambiguous
- Beyond: peak in wrong bin → systematic error

### Практична tolerance (SX1280):
- Total static offset: ±25% of BW
- Estimation range: ±B/4
- Crystal 20 ppm @ 868 MHz + 125 kHz BW: CFO ≈ ±17.3 kHz ≈ ±0.14N bins

### Приклад для SF12, BW=125 kHz:
- Bin width = 125000 / 4096 = **30.5 Hz**
- Failure при CFO ≥ **15.3 Hz** (0.5 bins)
- → CFO correction critical для high SF!

---

## 6. Symbol Timing Offset (STO) Impact

### Математика:
- STO = τ → frequency offset = B×τ
- **Integer STO:** Kronecker delta (energy peak) зміщується на discrete bins
- **Fractional STO:** energy scatter по adjacent bins (spectral leakage) + instantaneous phase jump = **-2π×λ_STO** на boundary

### Lightweight STO Estimation

| Алгоритм | Складність |
|----------|-----------|
| Up-Down Chirp Peak Comparison | L_STO = (ŝ_up - L_CFO) mod N |
| Three Spectral Lines (TSL) | Sub-bin precision, low complexity |
| Iterative Two-Pass | Pass 1: fractional CFO, Pass 2: λ_STO |

### Correction:
- Integer STO → shift sampling window start
- Fractional STO → resample або decimation index adjustment
- Phase correction → sample-by-sample rotation (SFO)

---

## 7. ELRS Preamble (8 up-chirps)

### Використання для confidence та noise suppression
1. **Coherent integration:** 8 identical up-chirps → теоретичний SNR gain = **9 dB**
2. **Frequency Stability check:** true preamble = однакові bin positions у consecutive windows
3. **Sync Word validation:** другорядна верифікація (pattern matching)

### Детектор pipeline:
```
Detect 8 consecutive up-chirps at same bin index
    → Peak consistency check (noise rejection)
    → Sync Word pattern match
    → → Preamble detected → trigger Stage 2
```

---

## 8. Паралельна vs Послідовна стратегія

| Параметр | GPU parallel | CPU sequential |
|----------|-------------|----------------|
| Channel concurrency | High (SDR gateway) | Low (single channel) |
| Latency | Deterministic (pinned memory) | Varies (early exit) |
| Throughput | 11.5× faster | 3× baseline (CoRa) |
| Power | High | Low (IoT end-node) |

**Наш вибір:** GPU parallel (RTX 3070, Stage 3).

**Критична примітка:** CPU bottleneck → 77% time on synchronous memory copies. Рішення: **Double Buffering** (CPU loads batch N+1 while GPU computes N).

---

## Висновки для Stage 3

1. **24 паралельних фільтри** (SF7-12 × 4 BW) через cuFFT
2. **CFO correction** в першому проході (fractional CFO via consecutive up-chirps)
3. **STO correction** TSL interpolation (sub-bin precision)
4. **Double buffering** для CPU-GPU overlap
5. **Pre-allocated cuFFT plans** для всіх 6 N values

---

## Посилання

- [[stage2-tz-dechirp-mf]] — ТЗ Stage 3 (Dechirp + MF)
- [[stage2-dechirp-queries]] — дослідницькі запити (Stage 3)
- [[02-tz1-dechirp-mf]] — аналіз TZ#1 (KB-2)
- [[stage2-arch-principles]] — DWT/CWT архітектура
- [[20-cic-lora-collision-decoding]] — CIC dechirp під collision
