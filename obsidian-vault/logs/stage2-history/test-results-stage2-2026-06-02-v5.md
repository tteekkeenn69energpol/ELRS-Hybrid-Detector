# Результати тестування Stage 2 — T2-retry-v4 (spec v5 / C2-fix-v5) — 2026-06-02

**Verdict: ❌ FAIL**

> T2-retry-v4: тестування після C2-fix-v5 (Welch PSD замість SST/CWT).
> Базові лінії: v1/v2/v3/v4 FAIL (всі random: SF≈17%, BW≈25%).

---

## Середовище

- ОС: `Linux-6.14.0-36-generic-x86_64-with-glibc2.39`
- Host: `tekken-Latitude-5580`
- CPU: `13th Gen Intel(R) Core(TM) i5-13600KF` (20 cores)
- Python: `3.12.3` (numpy 1.26.4, pywt, scipy)
- samp_rate: 30.72 MS/s · buffer: 50 ms = 1,536,000 samples
- BW: Welch PSD (N_total=65536, N_fft=4096, K=31, Hann, threshold=1.5, noise_freq_min=3.25MHz)
- DWT: Re(IQ), sym5/L4, bw_candidate від PSD, single-column search
- Сигнал: тайлований CSS up-chirp (offset=0, wrap-around), centered (f0=-BW/2..+BW/2)

---

## Ключові метрики (gate)

| Метрика | v1 | v2 | v3 | v4 | **v5** | Ціль | |
|---|---|---|---|---|---|---|---|
| SF accuracy @ SNR≥-10dB | 17% | 17% | 14% | 12.5% | **16.1%** | ≥85% | ❌ |
| BW accuracy @ SNR≥-12dB | 25% | 24% | 25% | 25.0% | **25.0%** | ≥80% | ❌ |
| SF+BW pair @ SNR=-14dB  | 5%  | 5%  | 4%  | 3.9% | **5.0%** | ≥78% | ❌ |
| Latency (100 reps, median) | 19ms✅ | 79ms❌ | 18ms✅ | 14.9ms✅ | **12.0ms** | ≤25ms | ✅ |
| False trigger rate (1000 AWGN) | 2%✅ | 0%✅ | 0%✅ | 0.0%✅ | **0.0%** | ≤5% | ✅ |

**BW accuracy = 25% — 5-та ітерація поспіль: BW=1625k передбачається у 100% випадків.**

---

## По BW (деталізація)

### BW prediction @ SNR=-12dB (N=300 per BW, 6 SFs × 50)

| True BW | Predicted 203k | Predicted 406k | Predicted 812k | Predicted 1625k | Accuracy |
|---|---|---|---|---|---|
| 203k | 0 | 0 | 0 | **300** | **0.0%** |
| 406k | 0 | 0 | 0 | **300** | **0.0%** |
| 812k | 0 | 0 | 0 | **300** | **0.0%** |
| 1625k | 0 | 0 | 0 | **300** | **100.0%** |

→ Повна деградація: ВСЯ енергія рішення — BW=1625k.
→ 100% для BW=1625k = не справжня точність, а bias до максимального класу.

---

## ROOT CAUSE F — Welch PSD spectral edge detection вразливий до chi-squared noise outliers

### Механізм збою

**1. Noise distribution (chi-squared)**

Welch PSD усереднює K=31 незалежних Hann-windowed frames. Шумові bins слідують chi-squared
розподілу з 2K=62 ступенями свободи:
- Mean = 1.0 × noise_floor (за нормалізацією)
- Std = √(2/K) = √(2/31) ≈ **25.4% of mean**
- P(S_norm > 1.5) = P(χ²₆₂ > 93) ≈ **0.26%** per bin

**2. Noise bins вище NOISE_FREQ_MIN**

```
freqs > noise_freq_min=3.25MHz → кількість bins ≈ (15360-3250)/7.5 ≈ 1614 bins
E[false positives] = 0.0026 × 1614 ≈ 4.2 bins per estimate
```

**3. f_edge = max(occupied)**

```python
occupied = freqs[S_norm > 1.5]           # включає noise outliers!
f_edge = max(occupied)                    # завжди noise outlier (high freq)
bw_raw = 2 × f_edge ≈ 2 × 14000kHz = 28000kHz >> 1625kHz
bw_candidate = min(target_bws, |b - 28000kHz|) → 1625k
```

**4. Наслідки**

```
BW=203k: S_norm[101kHz]=4.25 (правильно>1.5 ✓), але f_edge=13972kHz (noise outlier!)
         → bw_raw=27945kHz → BW=1625k ✗
BW=1625k: S_norm[812kHz]=1.48 < 1.5 (сигнал нижче порогу!), але f_edge=15000kHz (noise)
          → bw_raw=30000kHz → BW=1625k (збіг через bias, не через дійсну детекцію)
```

**5. Верифікація вимірюваннями**

```
Тест: BW=203k, SNR=-12dB, aligned (offset=0):
  noise_floor = 12036.4
  f_edge = 13972.5kHz   ← noise outlier (не 101.5kHz = BW/2!)
  bw_raw = 27945kHz     ← 137× вище BW
  BW prediction = 1625k ← завжди
```

### Аналіз порогу

Spec стверджує Z≥4.2σ @ BW=1625k @ -14dB. Але Z-score аналізував ТІЛЬКИ сигнал,
не ЙМОВІРНІСТЬ FALSE POSITIVE від noise outliers:

```
Signal (BW=1625k @ -14dB): S_norm[BW/2] ≈ 1 + 0.75 = 1.75 (barely above 1.5)
Noise outlier: S_norm[random_high_freq] ≈ 2.0-3.0 (chi-squared tail)
```

Для threshold=1.5 і K=31: частка noise bins, що перевищують поріг ≈ 0.26%.
З 1614 noise bins: ~4.2 false positives per estimate → f_edge ЗАВЖДИ вибирає false positive.

### Варіанти виправлення (для DSP Research R2-fix-v6)

**Опція A (рекомендована): Обмежити пошук частот до [0, max_bw/2=812.5kHz]**

```python
max_bw_half = max(target_bws) / 2  # = 812_500 Hz
search_mask = (freqs > 0) & (freqs <= max_bw_half)
occupied = freqs[search_mask & (S_norm > threshold)]
```

Переваги: усуває всі noise outliers вище 812kHz; просто; 108 bins замість 1614.
Ризик: threshold=1.5 дає 0.26% × 108 = 0.28 false positives per estimate → ~25% тестів
мають хибний false positive у [0, 812kHz]. Потребує threshold≈2.0 для P<5% FP.

Але threshold=2.0 може пропустити слабкий сигнал (BW=1625k @ -14dB: S_norm≈1.75 < 2.0).

**Опція B (надійна): Robust spectral edge — percentile замість max**

```python
occupied = freqs[S_norm > 1.5]
f_edge = np.percentile(occupied, 95)  # замість max(occupied)
```

Percentile=95 відкидає 5% outliers включно з noise-спайками у хвості.

**Опція C (найнадійніша): Обмеження + смуговий критерій**

```python
# Шукати edge тільки в [0, max_bw/2]
# f_edge = перша частота де rolling_median(S_norm, window=5) падає нижче 1.5
```

**Опція D: Збільшити K**

K=200 → std≈10% → P(S_norm>1.5) ≈ P(z>2.5) ≈ 0.6% → але z=5 for threshold=1.5→... 
Насправді: К=200, χ²₄₀₀: std=√(2/200)=10%; threshold=1.5 → z=(1.5-1)/0.1=5σ → P≈3e-7 per bin → 0 FP.
Але N_total = (200-1)×2048+4096 = 411,648 = 13.4ms → latency ≈ 15ms + DWT ~15ms = 30ms > 25ms! ❌

**Висновок по опціям**: Опція B або A+threshold_tuning — найбільш перспективні.
Потребує R2-fix-v6 (spec) + C2-fix-v6 (implementation).

---

## Latency (100 reps)

Median = **11.98 ms** · p95 = 12.42 ms · ✅ Gate PASS (≤25ms).

Welch PSD latency (65536 samples) ≈ 2ms. DWT (1.5M samples) ≈ 9ms. Total ≈ 11ms ✓.

---

## False Trigger Rate (1000 AWGN buffers)

- Triggered: 0/1000 · Rate: **0.0%** ✅ Gate PASS (≤5%).
- Note: FTR=0% тому що confidence=0.5×dwt+0.5×cwt залишається низьким для pure AWGN.

---

## Прогрес по версіях

| Компонент | v1 | v2 | v3 | v4 | **v5** |
|---|---|---|---|---|---|
| DWT normalization | ❌ | ✅ | ✅ | ✅ | ✅ |
| DWT lag ambiguity | ❌ | ❌ | ✅ | ✅ | ✅ |
| BW method | SST@|IQ| | SST@Re+wrong_scales | SST@Re+samp/BW | SST@Re+5/π×s/BW | **Welch PSD** |
| BW bias | all→203k | all→1625k | all→203k | all→203k | **all→1625k** |
| BW accuracy | 25% | 24% | 25% | 25% | **25%** |
| Latency | 19ms✅ | 79ms❌ | 18ms✅ | 15ms✅ | **12ms✅** |
| FTR | 2% | 0% | 0% | 0% | **0%** |

**5 ітерацій, BW accuracy не зрушується з 25% (random 1/4).**

---

## Висновок

❌ **FAIL** — 3 блокуючих метрики не пройдені:

| Метрика | Результат | Ціль | |
|---|---|---|---|
| SF accuracy @ -10dB | **16.1%** | ≥85% | ❌ |
| BW accuracy @ -12dB | **25.0%** (100%→BW=1625k) | ≥80% | ❌ |
| pair @ -14dB | **5.0%** | ≥78% | ❌ |
| Latency | **11.98 ms** | ≤25 ms | ✅ |
| FTR | **0.0%** | ≤5% | ✅ |

**ROOT CAUSE F:** `threshold=1.5` з `f_edge=max(occupied)` фундаментально broken при K=31 frames:
chi-squared noise outliers (~4.2 false positives з 1614 bins вище NOISE_FREQ_MIN) завжди
дають f_edge >> BW/2 → bw_raw >> 1625kHz → BW=1625k в 100% випадків.

Spec Z-score аналіз (§R2-2) розраховував SNR сигналу, але не враховував P(false positive)
від chi-squared шумових bins у `max(occupied)`.

→ **Потрібна R2-fix-v6 (DSP Research): robust spectral edge detection.**
→ **D2 заблоковано. Повернути до DSP Research → R2-fix-v6 → Python Dev → C2-fix-v6.**

---

_Run: 2026-06-02 · N=50/combo · 3 SNRs · 3600 estimates · latency 100 reps · FTR 1000 AWGN_
