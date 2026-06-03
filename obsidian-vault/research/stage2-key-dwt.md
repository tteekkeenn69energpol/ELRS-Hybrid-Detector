---
tags: [stage-2, knowledge-builder, dwt, sf-estimation, synthesis]
created: 2026-05-29
type: synthesis
stage: 2
status: done
---

# DWT для SF Estimation — Synthesis Note

Конспект ключових фактів про Discrete Wavelet Transform для оцінки Spreading Factor (SF 7–12) у Stage 2.

---

## Принцип роботи

DWT розкладає сигнал на approximation та detail coefficients через **dyadic filter bank**.

LoRa up-chirps мають **frequency wraps** на boundaries символів → локалізовані **energy surges** у high-freq Detail coefficients.

**Symbol duration:** `Ts = 2^SF / BW`

Кожен SF має унікальний **periodicity signature** у Detail coefficients.

---

## SF Estimation Pipeline

```python
signal = np.abs(iq_buffer)                    # magnitude (або real-part)
coeffs = pywt.wavedec(signal, wavelet, level=max_level)
detail = coeffs[target_level]                 # Level 3 або 4

# Autocorrelation → periodicity
autocorr = np.correlate(detail, detail, mode='full')
autocorr = autocorr[len(autocorr)//2:]

# Пік шукаємо біля symbol_len = 2^sf
for sf in range(7, 13):
    symbol_len = 2**sf
    peak_score = autocorr[symbol_len] / autocorr.mean()
    sf_scores[sf] = peak_score

best_sf = max(sf_scores, key=sf_scores.get)
```

Або через DWT-FFT (пряме):
```python
fft_of_detail = np.abs(np.fft.fft(detail))
# Пік на частоті fs_detail / (2^sf) → SF identification
```

---

## Вибір вейвлету

| Вейвлет | Performance | Рекомендація |
|---------|-------------|--------------|
| **sym5** | Хороший, smooth | TZ#2 default, практичний |
| **sym8** | Краще при -12 dB | Більші фільтри |
| **db4** | Стандартний | Широко протестований |
| **db8** | Denoising | Ізоляція HF шуму |
| **Biorthogonal** | Найкращий < -5 dB | Складніший, для edge cases |

**Поточний вибір:** `sym5` (TZ#2, [[stage2-tz-dwt-cwt]])
**Розглянути:** biorthogonal якщо SF accuracy < 85% при SNR = -10 dB

---

## Оптимальні рівні декомпозиції

| samp_rate | Oversampling (відносно BW=1625kHz) | Level |
|-----------|-----------------------------------|-------|
| 30.72 MS/s | ~19× | Level 4 |
| 100 MS/s | ~62× | Level 5–6 |

**Правило:** `target_level = floor(log2(samp_rate / bw_max)) - 1`

Для нашого проєкту (30.72 MS/s, BW max 1625 kHz): **Level 4** (oversampling ~19×).

---

## Вікно аналізу

**Оптимум:** 8 символів SF10 = `8 × 2^10 × (1/BW)` секунд.

При samp_rate = 30.72 MS/s, BW = 1625 kHz:
- SF10 symbol = 2^10 / 1625000 = **630 мкс** → ~19 354 семплів
- 8 × SF10 = **5.04 мс → ~154 830 семплів**
- Буфер 50 мс достатній (≈ 1.5M семплів при 30.72 MS/s)

---

## Mapping SF → peak position

При Level 4, 30.72 MS/s, BW = 203 kHz (мінімум):

| SF | symbol_len (samples) | Очікуваний DWT autocorr peak |
|----|---------------------|------------------------------|
| 7 | 2^7 × (30.72M / 203k) ≈ 19 370 | lag ≈ 19 370 / 16 ≈ 1211 |
| 8 | 2^8 × ... ≈ 38 740 | lag ≈ 2422 |
| 9 | ≈ 77 480 | lag ≈ 4843 |
| 10 | ≈ 154 960 | lag ≈ 9685 |
| 11 | ≈ 309 920 | lag ≈ 19 370 |
| 12 | ≈ 619 840 | lag ≈ 38 740 |

*Значення приблизні — точні треба відкалібрувати на синтетичних даних (T2-1)*

---

## Точність та обмеження

- **99.5% accuracy** при SNR ≥ -10 dB (confirmed by [[stage2-arch-principles]])
- **Detection floor:** ~-10 dB для reliable; до -20 dB для SF9–10
- **Limitation:** Dyadic resolution → BW оцінка обмежена power-of-two sub-bands
- **Harmonic interference:** DWT filter transition-bands → false peaks у HF

---

## GPU реалізація

DWT (pywt.wavedec) — **CPU є достатнім** для Stage 2 через низький duty cycle (~1–5%).

Якщо треба GPU: `cupy` + CuDWT або кастомний CUDA kernel (lifted wavelet filter bank).

---

## Посилання

- [[stage2-arch-principles]] — NotebookLM: детальний аналіз DWT для LoRa
- [[stage2-dwt-cwt-questions]] — Q1, Q4, Q10, Q11, Q20, Q25
- [[stage2-tz-dwt-cwt]] — ТЗ (код референс)
- [[03-tz2-dwt-cwt]] — попередній аналіз (KB-2)
- [[09-stage2-blind-estimator-py]] — Python implementation reference
- [[stage2-key-cwt]] → наступний крок після SF estimation
- [[stage2-key-confidence-gate]] → gate після SF+BW estimation
