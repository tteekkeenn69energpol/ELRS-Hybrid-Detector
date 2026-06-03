# Результати тестування Stage 2 — Blind Estimator — T2-retry — 2026-06-02

**Verdict: ❌ FAIL**

> T2-retry після C2-fix (2026-06-02). Порівняння з FAIL v1 (2026-05-29).

---

## Середовище

- ОС: `Linux-6.14.0-36-generic-x86_64-with-glibc2.39`
- Host: `tekken-Latitude-5580`
- CPU: `13th Gen Intel(R) Core(TM) i5-13600KF` (20 cores)
- Python: `3.12.3` (numpy 1.26.4, pywt, ssqueezepy, scipy)
- samp_rate: 30.72 MS/s · buffer: 50 ms = 1,536,000 samples
- Wavelet: sym5 · DWT level: 4 · CWT: Morlet+SST · Scales: geomspace(N_sym_min, N_sym_max, 4)

---

## Ключові метрики (gate)

| Метрика | v1 FAIL | v2 C2-fix | Ціль | Статус |
|---|---|---|---|---|
| SF accuracy @ SNR≥-10dB | ~17% (random) | **~16–17%** (random) | ≥85% | ❌ |
| BW accuracy @ SNR≥-12dB | 25% (random) | **~24%** (random) | ≥80% | ❌ |
| SF+BW pair @ SNR=-14dB  | ~5% (random) | **~5%** (random) | ≥78% | ❌ |
| Latency (median, 10 reps) | 19.14 ms ✅ | **79.45 ms** ❌ | ≤25 ms | ❌ ПОГІРШИЛАСЬ |
| False trigger rate (info) | 2.0% ✅ | **0.0%** ✅ | ≤5% | ✅ |

> ⚠️ Latency ПОГІРШИЛАСЬ з 19ms до 79ms через нові великі scales у CWT — нова блокуюча проблема.

---

## Параметри тестування

| Параметр | Значення |
|---|---|
| N probe (accuracy) | 20/combo × 24 combos × 2 SNR = 960 estimates |
| SNRs тестовані | -10 dB, 0 dB |
| threshold_low/high | 0.0 / 1.1 (вимкнено для accuracy) |
| holdoff | 0.0 (вимкнено) |
| Latency N | 10 reps, SF=9/BW=812k/SNR=0dB |
| False trigger N | 200 AWGN buffers |

---

## Детальний аналіз точності

### SF Accuracy

| SNR (dB) | SF Accuracy | vs v1 |
|---|---|---|
| -10 | ~16.2% | ≈ без змін (v1: ~17%) |
| 0   | ~17.3% | ≈ без змін |

**SF prediction distribution (SNR=-10dB, N=480):**
```
SF7:  148 (31%)  ← домінує (зміщення до нижнього SF)
SF8:   75 (16%)
SF9:   35 (7%)
SF10:  85 (18%)
SF11:  59 (12%)
SF12:  78 (16%)
```
Розподіл нерівномірний, але не в правильному напрямку (≠ від щоправда передбаченого).

### BW Accuracy

| SNR (dB) | BW Accuracy | vs v1 |
|---|---|---|
| Всі | ~24% | ≈ без змін (v1: 25%) |

**BW prediction distribution (SNR=-10dB, N=480):**
```
BW=203k:   5  (1%)
BW=406k:   22 (5%)
BW=812k:  166 (35%)
BW=1625k: 287 (60%) ← домінує (vs v1 де домінував BW=203k)
```
Зміщення змінилось напрямок (v1: завжди 203k, v2: завжди 1625k), але обидва = системний збій.

---

## Аналіз C2-fix — Що пішло не так

### Bug #1 fix (dwt_estimator.py) — Частково правильний

**Що зроблено:**
```python
autocorr_norm = float(np.mean(np.abs(autocorr[lag_min:lag_max + 1])))
autocorr_norm = max(autocorr_norm, 1e-12)
```
Нормалізація виправлена — `mean(|autocorr|)` завжди > 0. ✓

**Проблема, що залишилась — фундаментальна LAG AMBIGUITY:**

З таблиці _LAG_TABLE, ці (SF, BW) пари мають **ОДНАКОВИЙ lag**:
```
lag=1211: (SF7, BW203k), (SF8, BW406k), (SF9, BW812k) — однаковий lag!
lag=2422: (SF8, BW203k), (SF9, BW406k), (SF10, BW812k)
lag=4843: (SF9, BW203k), (SF10, BW406k), (SF11, BW812k), (SF12, BW1625k)
lag=9686: (SF10, BW203k), (SF11, BW406k), (SF12, BW812k)
```

Символьна тривалість `2^SF/BW` ОДНАКОВА для цих пар! DWT autocorr не може їх розрізнити.
З `if score > best_score` (строге >): рівні scores → перший у порядку ітерації виграє → завжди SF=7.

**Причина погіршення:**
Ці пари є ambiguous тому що `2^SF/BW` = const → той самий lag → той самий autocorr score.
Виправлення нормалізації не вирішує цю фундаментальну неоднозначність.

**Також: DWT на |IQ| проблематичне для constant-amplitude CSS chirp:**
- CSS chirp: |chirp(t)| = 1 скрізь (constant envelope)
- При додаванні AWGN: |chirp + noise| ≈ 1 + gaussian fluctuations (white noise in magnitude)
- DWT detail coefficients від |IQ| відображають переважно шумові флуктуації, не символьні межі
- Автокореляційний пік на символьному лагу СЛАБКИЙ у порівнянні з шумовим фоном

---

### Bug #2 fix (cwt_estimator.py) — Неправильна формула scales

**Що зроблено (C2-fix):**
```python
min_s = samp_rate * (2 ** sf_candidate) / max(target_bws)  # N_sym_min
max_s = samp_rate * (2 ** sf_candidate) / min(target_bws)  # N_sym_max
scales_arr = np.geomspace(min_s, max_s, len(target_bws))
signal = np.real(iq_window)  # ← Re(IQ) замість |IQ|
```

**Проблема — НЕПРАВИЛЬНИЙ діапазон частот:**

| Scale | Center freq (Morlet, w₀=5, fs=30.72MS/s) | Chirp IF range |
|---|---|---|
| 9,685 | 2.5 kHz | — |
| 19,373 | 1.3 kHz | — |
| 38,732 | 0.6 kHz | — |
| 77,480 | 0.3 kHz | — |
| **CSS chirp (BW=812k)** | **−406 kHz..+406 kHz** | ← зовсім інший діапазон! |

Formula `scale = samp_rate × 2^SF / BW = N_sym` = symbol duration in samples.
У Morlet CWT: center frequency = w₀ × samp_rate / (2π × scale) = w₀ × BW / (2π × 2^SF).
Для SF=9, BW=812k: f_c = 5 × 812000 / (2π × 512) ≈ **1.26 kHz** — в 300 разів нижче від BW!

→ CWT фільтрує near-DC частини сигналу (0.3–2.5 kHz), де є лише noise.
→ Energy ≈ однакова на всіх scales → випадковий BW (зі зміщенням до smallest scale = BW=1625k).
→ SST також не застосовується (`sst_used=False` у всіх тестах).

**Наслідок для latency:**
```python
min_needed = max(cwt_max_samples, int(3 * min_s))
# SF=9: min_needed = max(8192, 3×9685) = 29055 samples (було 8192)
# SF=12: min_needed = max(8192, 3×77490) = 232470 samples!
```
CWT тепер обробляє 3.6–28.4× більше samples → latency 79ms замість 19ms.

---

## Latency (T2-5)

| Rep | Latency (ms) |
|---|---|
| 1  | 96.60 |
| 2  | 90.23 |
| 3  | 97.13 |
| 4  | 78.10 |
| 5  | 77.64 |
| 6  | 79.40 |
| 7  | 78.09 |
| 8  | 82.01 |
| 9  | 77.94 |
| 10 | 79.49 |

**Median = 79.45 ms** · std = 7.49 ms · min = 77.64 ms · max = 97.13 ms

❌ Gate FAIL (79.45 ms >> 25 ms). **Погіршилась у 4.1× відносно v1 (19.14 ms).**

**Причина:** N_sym scales (9685–232470) → `min_needed = 3 × min_s` значно більше ніж 8192.

---

## False Trigger Rate (T2-6)

- AWGN buffers tested: 200
- Triggered (conf ≥ 0.4): 0
- Rate: **0.0%** ≤5% ✅

---

## Маршрут виправлення

### Потрібне виправлення DSP Research (R2-fix-v3)

**Проблема A — DWT lag ambiguity:**

Пари `{2^SF/BW = const}` є фундаментально нерозрізнені через DWT одного рівня:
```
(SF7, BW203k) = (SF8, BW406k) = (SF9, BW812k) → lag=1211
```
Рішення (DSP Research вибирає):
1. **Lookup-only**: якщо DWT знаходить lag=L, він безпосередньо дає BW через таблицю при ВІДОМОМУ SF → але SF невідомий a priori
2. **Multi-harmonic**: перевірити 2×lag, 4×lag → різні SF/BW пари мають різне harmonic structure
3. **Instantaneous freq**: `IF = diff(unwrap(angle(IQ))) × samp_rate/(2π)` → max-min = BW, rate = BW/2^SF → розрізняє SF та BW

**Проблема B — CWT scale formula:**

Правильна формула для Morlet center freq = f_target:
```
scale = w₀ × samp_rate / (2π × f_target)
```

Для CSS chirp (Re(IQ) sweeping ±BW/2), f_target ≈ BW/4 (quartile of positive IF):
```
BW=203k: scale = 5 × 30.72e6 / (2π × 50.75k) ≈ 482
BW=406k: scale ≈ 241
BW=812k: scale ≈ 120
BW=1625k: scale ≈ 60
```
Такі scales близькі до v1 [151, 76, 38, 19] але коректніші для f_target = BW/4.

**⚠️ ВАЖЛИВО:** Навіть з правильними scales, CWT energy contrast між BW класами є СЛАБКИМ (~1.1-1.3×) при SNR=0dB. DSP Research має оцінити, чи CWT Morlet взагалі підходить для CSS BW estimation через Re(IQ), або потрібен альтернативний підхід (inst_freq, dechirp, STFT slope).

**Проблема C — Latency:**

Обмежити `min_needed` константою незалежно від scale:
```python
iq_window = iq_np[:cwt_max_samples]  # WITHOUT 3×min_s expansion
signal = np.real(iq_window).astype(np.float64)
```
Повернутись до `cwt_max_samples=8192` або збільшити помірно (≤16384).

### Для Python Dev (C3-fix, після R2-fix-v3)

1. `cwt_estimator.py`:
   - Scale formula: `scale = w₀ × samp_rate / (2π × (BW/4))` (або за spec від DSP Research)
   - Повернутись до `iq_window = iq_np[:cwt_max_samples]` без 3×min_s
   - Залишити `signal = np.real(iq_window)` (це правильно)

2. `dwt_estimator.py`:
   - Нормалізація вже правильна — залишити
   - Можливо: після виявлення peak-lag, повернути весь список (SF, BW) з цим lag → передати в CWT для вибору

3. `blind_estimator.py`:
   - Cascade logic — залишити (передача sf_candidate в CWT правильна)

---

## Висновок

❌ **FAIL** — 4 з 4 блокуючих gate провалені:

| Метрика | Результат | Ціль | Статус |
|---|---|---|---|
| SF accuracy @ -10dB | **~17%** (random) | ≥85% | ❌ |
| BW accuracy @ -12dB | **~24%** (random) | ≥80% | ❌ |
| SF+BW pair @ -14dB  | **~5%** (random) | ≥78% | ❌ |
| Latency median      | **79.45 ms** | ≤25 ms | ❌ ↑4× від v1 |
| False trigger rate  | 0.0% | ≤5% | ✅ |

C2-fix не вирішив жодного блокуючого бага:
- Bug #1 (DWT нормалізація): формула правильна, але фундаментальна lag-ambiguity залишилась
- Bug #2 (CWT scale): signal=Re(IQ) правильно, але scale=N_sym дає center freq 100-1000× нижче від chirp IF → CWT сліпа до BW + latency 4× гірше

→ **Потрібен R2-fix-v3 (DSP Research) + C3-fix (Python Dev). D2 заблоковано.**

---

## Артефакти

- `tests/stage2/synth_dataset.py` — T2-1 ✅
- `tests/stage2/test_sf_accuracy.py` — готовий до повторного запуску
- `tests/stage2/test_bw_accuracy.py` — готовий до повторного запуску
- `tests/stage2/run_stage2_tests.py` — master runner
- `tests/stage2/test-results-stage2.md` — FAIL v1 звіт (базова лінія)
- `tests/stage2/test-results-stage2-retry.md` — цей файл (FAIL v2)
- `obsidian-vault/logs/test-results-stage2-2026-06-02.md` — копія

## Відтворення

```bash
cd /home/tekken/ELRS_Hybrid_Detector_Vault/ELRS_Hybrid_Detector_Vault
# Quick probe (N=20/combo, 2 SNRs):
python3 -c "
import sys
sys.path.insert(0, 'src/stage2')
sys.path.insert(0, 'tests/stage2')
import numpy as np
from blind_estimator import ELRS_BlindParameterEstimator
from synth_dataset import make_iq_buffer, SFS, BWS
rng = np.random.default_rng(123)
est = ELRS_BlindParameterEstimator(samp_rate=30.72e6, threshold_low=0.0, threshold_high=1.1, holdoff_s=0.0)
n = 20; total = 0; sf_ok = 0
for sf in SFS:
    for bw in BWS:
        for _ in range(n):
            buf = make_iq_buffer(sf, bw, snr_db=-10, rng=rng)
            res = est.estimate(buf)
            if res['sf']==sf and res['bw']==bw: sf_ok += 1
            total += 1
print(f'SF+BW pair: {sf_ok/total:.1%} (gate ≥78%)')
"
```

_Run timestamp: 2026-06-02 · N=20 probe (sufficient for systematic failure detection)_
