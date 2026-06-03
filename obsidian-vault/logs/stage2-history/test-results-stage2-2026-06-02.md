# Результати тестування Stage 2 — T2-retry-v2 (spec v3 / C2-fix-v3) — 2026-06-02

**Verdict: ❌ FAIL**

> T2-retry-v2: тестування після C2-fix-v3 (CWT-first, scales=[151,76,38,19], Re(IQ), window=8192).
> Базові лінії: v1 FAIL (2026-05-29), v2 FAIL (2026-06-02 retry).

---

## Середовище

- ОС: `Linux-6.14.0-36-generic-x86_64-with-glibc2.39`
- Host: `tekken-Latitude-5580`
- CPU: `13th Gen Intel(R) Core(TM) i5-13600KF` (20 cores)
- Python: `3.12.3` (numpy 1.26.4, pywt, ssqueezepy, scipy)
- samp_rate: 30.72 MS/s · buffer: 50 ms = 1,536,000 samples
- CWT: Re(IQ[:8192]), Morlet+SST, scales=[151,76,38,19]
- DWT: Re(IQ), sym5/L4, bw_candidate від CWT, single-column search

---

## Ключові метрики (gate)

| Метрика | v1 | v2 | **v3** | Ціль | Статус |
|---|---|---|---|---|---|
| SF accuracy @ SNR≥-10dB | 17% | 17% | **13.6%** | ≥85% | ❌ |
| BW accuracy @ SNR≥-12dB | 25% | 24% | **25.0%** | ≥80% | ❌ |
| SF+BW pair @ SNR=-14dB  | 5%  | 5%  | **3.6%** | ≥78% | ❌ |
| Latency (median, 10 reps) | 19.1ms✅ | 79ms❌ | **18.1ms** | ≤25 ms | ✅ ВІДНОВЛЕНО |
| False trigger rate (info) | 2.0%✅ | 0%✅ | **0.0%** | ≤5% | ✅ |

**C2-fix-v3 частково відновив latency** (79ms → 18ms), але точність залишилась на рівні
випадкового вгадування для всіх трьох блокуючих метрик.

---

## Параметри тестування

| Параметр | Значення |
|---|---|
| N probe (accuracy) | 15/combo × 24 combos × 6 SNRs = 2,160 estimates |
| SNRs тестовані | -14, -12, -10, -6, 0, +6 dB |
| threshold_low/high | 0.0 / 1.1 (вимкнено для accuracy) |
| holdoff | 0.0 (вимкнено) |
| Latency N | 10 reps, SF9/BW812k/SNR=0dB |
| False trigger N | 200 AWGN buffers |

---

## Детальний аналіз точності (по SNR)

| SNR (dB) | SF accuracy | BW accuracy | Pair accuracy |
|---|---|---|---|
| -14 | 13.9% | 25.0% | 3.6% |
| -12 | 13.3% | 25.0% | 4.2% |
| -10 | 13.6% | 25.0% | 2.8% |
| -6  | 18.3% | 25.3% | 5.6% |
| 0   | 15.0% | 25.0% | 5.8% |
| +6  | 13.6% | 25.0% | 4.2% |

**Висновок:** Точність не залежить від SNR — характеристика системного збою, не SNR-деградації.

---

## Аналіз confusion patterns (SF та BW)

### BW prediction @ SNR=-10dB (N=360 estimates)

| Predicted BW | Count | % |
|---|---|---|
| **BW=203k** | **359** | **99.7%** |
| BW=1625k | 1 | 0.3% |
| BW=406k | 0 | 0% |
| BW=812k | 0 | 0% |

→ CWT з SST завжди повертає BW=203k (scale=151 домінує).
→ BW accuracy = 25% = 1/4 = частка тестів з true BW=203k.

### SF prediction @ SNR=-10dB (N=360 estimates)

| Predicted SF | Count | % |
|---|---|---|
| SF7  | 41 | 11.4% |
| SF8  | 111 | 30.8% |
| SF9  | 55 | 15.3% |
| SF10 | 53 | 14.7% |
| SF11 | 60 | 16.7% |
| SF12 | 40 | 11.1% |

→ Розподіл нерівномірний але без чіткого правильного SF.
→ DWT отримує bw_candidate=203k → шукає SF в колонці BW=203k:
   лаги [1211, 2422, 4843, 9686, 19373, 38745] — **6 унікальних лагів, але лише для BW=203k.**
   Для тестів із true BW≠203k DWT шукає за неправильними лагами → хаотичний SF.

---

## Root cause аналіз — чому v3 CWT все ще не працює

### CWT фундаментальна проблема: scale formula samp_rate/BW

Scales = [151, 76, 38, 19] відповідають Morlet center frequencies:

```
f_c(scale) = w₀ × samp_rate / (2π × scale) = 5 × samp_rate / (2π × scale)

scale=151 → f_c = 162 kHz   (spec: BW=203k, chirp IF: 0..101.5 kHz)
scale=76  → f_c = 322 kHz   (spec: BW=406k, chirp IF: 0..203 kHz)
scale=38  → f_c = 643 kHz   (spec: BW=812k, chirp IF: 0..406 kHz)
scale=19  → f_c = 1290 kHz  (spec: BW=1625k, chirp IF: 0..812 kHz)
```

**Мeta-проблема:** scale=samp_rate/BW → f_c = w₀×BW/(2π) ≈ **0.796×BW**.
CSS chirp sweeps ±BW/2 → max positive IF = BW/2. Але f_c ≈ **1.59×(BW/2)** — у 1.59× вище!

Морлет не "бачить" chirp — center frequency вище за максимальну IF chirp.

**Результат: energy analysis (аналітичний):**

Для кожного scale та кожного true BW, перекриття = Φ((BW_max_IF - f_c) / σ):

| True BW | scale=151 (f_c=162k) | scale=76 (f_c=322k) | scale=38 (f_c=643k) | scale=19 (f_c=1290k) | Predicted |
|---|---|---|---|---|---|
| 203k (IF:0..101.5k) | 3.1% | 0.03% | ~0% | ~0% | 203k ✓ |
| 406k (IF:0..203k)   | **90%** | 3.2% | 0.03% | ~0% | **203k ✗** |
| 812k (IF:0..406k)   | **~100%** | **90%** | 3.3% | ~0% | **203k ✗** |
| 1625k (IF:0..812k)  | **~100%** | **~100%** | 91% | 3.3% | **203k ✗** |

→ scale=151 (BW=203k) **завжди** перемагає, бо всі chirps мають IF частково під f_c=162k.
→ Навіть при true BW=1625k: scale=151 має 100% перекриття з chirp IF range [0, 812k].
→ SST підсилює low-frequency компоненти → ще більше bias до scale=151.

**Перевірено емпірично:**
- SST (`ssqueezepy.ssq_cwt`): BW=203k передбачається у 99.7% випадків ✗
- Plain CWT (scipy): BW=1625k передбачається у ~100% випадків ✗ (різний bias)

### Що треба виправити

**Правильна scale formula** для Morlet detection CSS chirp з max IF = BW/2:

```
f_c = BW/2  →  scale = w₀ × samp_rate / (2π × BW/2) = w₀ × samp_rate / (π × BW)
             = 5 × samp_rate / (π × BW)
```

| BW | Правильний scale | Поточний (samp_rate/BW) | Зміна |
|---|---|---|---|
| 203k | **481** | 151 | +3.2× |
| 406k | **241** | 76 | +3.2× |
| 812k | **120** | 38 | +3.2× |
| 1625k | **60** | 19 | +3.2× |

З правильними scales [481, 241, 120, 60]:
- f_c(481) = 5×30.72e6/(2π×481) = 50.8kHz = BW/4 (for BW=203k)

Hmm, це все одно off по factor 2. Потрібно `scale = 5×samp_rate/(π×BW)`, що дає f_c = BW/2:
- BW=203k: scale=481, f_c=5×30.72e6/(2π×481)=50.8kHz...

Стоп, давайте перевіримо: `f_c = w₀/(2π×scale) × samp_rate`:
Хочемо f_c = BW/2. Отже scale = w₀×samp_rate/(2π×(BW/2)) = 2×w₀×samp_rate/(2π×BW) = w₀×samp_rate/(π×BW).
= 5×30.72e6/(π×203000) = 240.8 → scale≈241 для BW=203k.

| BW | Правильний scale (f_c=BW/2) |
|---|---|
| 203k | **241** (f_c=101.5kHz ✓) |
| 406k | **121** (f_c=203kHz ✓) |
| 812k | **60** (f_c=406kHz ✓) |
| 1625k | **30** (f_c=812kHz ✓) |

З цими scales Morlet center = chirp max positive IF. Discrimination буде максимальним.

**Для DSP Research (R2-fix-v4):**
```python
# Правильна формула: f_c = BW/2 → scale = w₀ × samp_rate / (π × BW)
scales = [round(5 * samp_rate / (np.pi * bw)) for bw in target_bws]
# = [241, 121, 60, 30] для samp_rate=30.72 MS/s
```

---

## Latency (T2-5) — відновлено!

| Rep | Latency (ms) |
|---|---|
| 1  | 18.68 |
| 2  | 17.97 |
| 3  | 18.06 |
| 4  | 18.03 |
| 5  | 18.55 |
| 6  | 18.27 |
| 7  | 18.23 |
| 8  | 17.62 |
| 9  | 17.44 |
| 10 | 15.14 |

**Median = 18.05 ms** · std = 0.96 ms · min = 15.14 ms · max = 18.68 ms

✅ Gate PASS (18.05 ms ≤ 25 ms). Відновлено від 79ms регресії v2. ✓

---

## False Trigger Rate (T2-6)

- AWGN buffers tested: 200
- Triggered (conf ≥ 0.4): 0
- Rate: **0.0%** ≤5% ✅

---

## Прогрес по версіях

| Компонент | v1 | v2 | v3 | Статус |
|---|---|---|---|---|
| DWT normalization | ❌ mean(autocorr) | ✅ mean(\|autocorr\|) | ✅ mean(\|autocorr\|) | Виправлено |
| DWT input | \|IQ\| | Re(IQ) | Re(IQ) | Виправлено |
| DWT lag ambiguity | ❌ 24 cols → 6 unique | ❌ 24 cols → 6 unique | ✅ 1 col → 6 unique | Виправлено (але CWT→203k) |
| CWT input | ❌ \|IQ\| | ✅ Re(IQ) | ✅ Re(IQ) | Виправлено |
| CWT window | 8192 ✅ | 3×N_sym ❌ | 8192 ✅ | Відновлено |
| CWT scale formula | ❌ samp_rate/BW@near-DC | ❌ N_sym@3kHz | ❌ samp_rate/BW@2×BW | **ЗАЛИШАЄТЬСЯ НЕПРАВИЛЬНИМ** |
| Latency | 19ms ✅ | 79ms ❌ | 18ms ✅ | Відновлено |
| BW accuracy | 25% (all→203k) | 24% (all→1625k) | 25% (all→203k) | Без змін |
| SF accuracy | 17% | 17% | 14% | Без змін |

---

## Висновок

❌ **FAIL** — 3 з 4 блокуючих gate провалені:

| Метрика | Результат | Ціль | |
|---|---|---|---|
| SF accuracy @ -10dB | 13.6% | ≥85% | ❌ |
| BW accuracy @ -12dB | 25.0% (all→203k) | ≥80% | ❌ |
| pair @ -14dB | 3.6% | ≥78% | ❌ |
| Latency | 18.05 ms | ≤25 ms | ✅ |

**Залишається одна незакрита root cause:**
CWT scale formula `samp_rate/BW` → center frequency = `0.796×BW`, що у **1.59×** вище за max chirp IF (BW/2).
Всі BWs отримують однаково "широкий" overlap від scale=151 (largest scale → lowest f_c → best coverage).
→ scale=151 завжди виграє → BW=203k завжди передбачається.

**Правильна формула (для R2-fix-v4):**
`scale = w₀ × samp_rate / (π × BW) = 5 × samp_rate / (π × BW)`
→ scales = [241, 121, 60, 30], де f_c = BW/2 (matched до max chirp IF).

→ **Повернути до DSP Research (R2-fix-v4: виправити scale formula)** + **Python Dev (C2-fix-v4: scale = 5×samp_rate/(π×BW))**.

---

## Артефакти

- `tests/stage2/synth_dataset.py` — T2-1 ✅ (CSS wrap-around correct)
- `tests/stage2/test_sf_accuracy.py` — готовий до повторного запуску
- `tests/stage2/test_bw_accuracy.py` — готовий до повторного запуску
- `tests/stage2/run_stage2_tests.py` — master runner
- `tests/stage2/test-results-stage2.md` — FAIL v1
- `tests/stage2/test-results-stage2-retry.md` — FAIL v2
- `tests/stage2/test-results-stage2-v3.md` — **цей файл** (FAIL v3)
- `obsidian-vault/logs/test-results-stage2-2026-06-02.md` — копія (оновлена)

---

_Run timestamp: 2026-06-02 · N=15 probe per combo, 6 SNR levels, 2160 total estimates_
