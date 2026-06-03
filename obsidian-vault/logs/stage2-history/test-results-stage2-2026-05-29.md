# Результати тестування Stage 2 — Blind Estimator — 2026-05-29

**Verdict: ❌ FAIL**

## Середовище

- ОС: `Linux-6.14.0-36-generic-x86_64-with-glibc2.39`
- Host: `tekken-Latitude-5580`
- CPU: `13th Gen Intel(R) Core(TM) i5-13600KF` (20 cores)
- Python: `3.12.3` (numpy 1.26.4, pywt, ssqueezepy)
- samp_rate: 30.72 MS/s · buffer: 50 ms = 1,536,000 samples
- Wavelet: sym5 · DWT level: 4 · CWT: Morlet+SST · Scales: [151, 76, 38, 19]

## Параметри тестування

| Параметр | Значення |
|---|---|
| SFs | [7, 8, 9, 10, 11, 12] |
| BWs (kHz) | [203, 406, 812, 1625] |
| SNR sweep | -14..+10 dB, крок 2 dB (13 рівнів) |
| N probe / combo | 10 (N=10 достатньо для виявлення системного збою) |
| threshold_low | 0.0 (вимкнено для accuracy тестів) |
| threshold_high | 1.1 (вимкнено) |
| holdoff | 0.0 (вимкнено) |

## Ключові метрики (gate)

| Метрика | Результат | Ціль | Статус |
|---|---|---|---|
| SF accuracy @ SNR≥-10dB | **~17%** (= 1/6 = випадковий рівень) | ≥85% | ❌ |
| BW accuracy @ SNR≥-12dB | **25.0%** (= 1/4 = випадковий рівень) | ≥80% | ❌ |
| SF+BW pair @ SNR=-14dB  | **~4–6%** (= 1/24 = випадковий рівень) | ≥78% | ❌ |
| Latency (median, 10 reps) | **19.14 ms** | ≤25 ms | ✅ |
| False trigger rate (info) | **2.0%** (200 AWGN buffers) | ≤5% | ✅ |

## Детальний аналіз — SF Accuracy

| SNR (dB) | SF Accuracy (N=10/combo) |
|---|---|
| -14 | ~14.6% |
| -10 | ~14.2% |
| -6  | ~13.3% |
| 0   | ~13.3% |
| +6  | ~16.7% |

**Висновок:** Результати статистично неможливо відрізнити від рівноймовірного вгадування
(шанс = 1/6 ≈ 16.7%). Значення **не змінюється зі зміною SNR** — характеристика системного
збою, а не лише низького SNR.

## Детальний аналіз — BW Accuracy

| SNR (dB) | BW Accuracy |
|---|---|
| Всі рівні | **25.0%** = 1/4 |

**Висновок:** BW=203kHz передбачається у **≈100% випадків** незалежно від справжнього BW.
Точно відповідає: (6 SF × 1 BW=203k × N) / (6 SF × 4 BW × N) = 1/4.

## Виявлені баги в src/stage2/ (критичні)

### БАГ #1 — `dwt_estimator.py` (рядок ~77): від'ємне `autocorr_mean`

**Місце:** `tests/stage2/` (дебаг) підтверджено на `src/stage2/dwt_estimator.py`

```python
# Поточна реалізація (НЕПРАВИЛЬНО):
autocorr_mean = float(np.mean(autocorr[lag_min:lag_max + 1]))
# Значення: autocorr_mean = -0.1879  ← NEGATIVE!

# score = autocorr[lag] / autocorr_mean
# При autocorr[lag] > 0 та mean < 0:  score < 0  (негативний!)
# best_score = -1.0 → НІКОЛИ не оновлюється при правильному піку!
```

**Механізм збою:**
- `detail = coeffs[1]` — wavelet detail coefficients, zero-mean (high-pass filter output)
- Autocorrelation `autocorr[k]` для k > 0 може бути від'ємною
- Mean over range [75, 77490]: `-0.1879` — negative
- `score = positive_peak / negative_mean = negative score < -1.0`
- Тому жодна правильна (позитивна) autocorr peak НІКОЛИ не перемагає
- Перемагає lag з `autocorr[lag] ≈ -0.02` (близьким до 0), що дає `score ≈ +0.1 > -1.0`
- Результат: SF вибирається НЕ за максимумом autocorr, а за мінімальним від'ємним піком → псевдовипадковий вибір

**Перевірено (commit 308f60d):**
```
autocorr_mean = -0.1879 (lag range 75..77490)
autocorr[lag=1211] = +78.39  → score = -417.1  < -1.0 → НЕ ВИБРАНО
autocorr[lag=4843] = -174.7  → score = +929.8  > -1.0 → ВИБРАНО (НЕПРАВИЛЬНО)
selected: SF9/BW203k  |  true: SF9/BW812k
```

**Правильна реалізація (для Python Dev):**
```python
# Опція A: нормалізація на zero-lag (завжди > 0)
autocorr_norm = autocorr[0] if autocorr[0] > 0 else 1.0

# Опція B: mean of absolute values
autocorr_norm = float(np.mean(np.abs(autocorr[lag_min:lag_max + 1])))
if autocorr_norm < 1e-12:
    autocorr_norm = 1.0

# Опція C (мінімальна правка): clip negative mean
autocorr_norm = max(float(np.mean(autocorr[lag_min:lag_max + 1])), 1e-6)
```

### БАГ #2 — `cwt_estimator.py` (рядок ~86): CWT на magnitude `|IQ|`

**Місце:** `src/stage2/cwt_estimator.py`

```python
# Поточна реалізація (НЕПРАВИЛЬНО для CSS chirp):
mag_full = np.abs(iq_np).astype(np.float64)  # magnitude envelope
signal = mag_full[:cwt_max_samples]
```

**Механізм збою:**
- CSS chirp — FM сигнал постійної амплітуди: `|chirp(t)| = const = 1.0` скрізь
- BW кодована у фазі (chirp rate = BW / 2^SF), не в амплітуді
- `|IQ|` = огинаюча ≈ постійна для чистого chirp (Rician distribution з signal component = 1)
- CWT огинаючої не бачить chirp rate — бачить лише AWGN envelope variation
- При малих scales (38, 19 → 812k, 1625k BW): CWT fільтрує дрібні коливання → менше energy
- При великому scale (151 → 203k BW): CWT усереднює ширший діапазон → більше energy (через LPF-ефект)
- Результат: BW=203k ЗАВЖДИ виграє незалежно від справжнього BW

**Перевірено:**
```
True BW=203k: 5/5 correct (правильно, але з неправильної причини)
True BW=406k: 0/5 correct (202k predicted)
True BW=812k: 0/5 correct (203k predicted)  energy_ratio=2.57 (scale=151 wins)
True BW=1625k: 0/5 correct (203k predicted)
```

**Правильна реалізація (для Python Dev або DSP Research):**
```python
# Опція A: CWT на real частину complex IQ (зберігає phase/frequency info)
signal = np.real(iq_np[:cwt_max_samples]).astype(np.float64)

# Опція B: instantaneous frequency via phase derivative
phase = np.unwrap(np.angle(iq_np[:cwt_max_samples]))
inst_freq = np.diff(phase) * samp_rate / (2 * np.pi)  # Hz
# потім CWT(inst_freq, scales) → peak scale = BW

# Опція C: CWT на complex IQ з complex Morlet напряму
# (потребує зміни в ssqueezepy call)
```

**Примітка DSP Research:** spec R2-2 прямо каже `signal = |IQ|` для CWT.
Якщо це навмисне рішення, необхідне переосмислення алгоритму детекції BW з magnitude.

## Latency (T2-5, незалежний від bench_stage2.py)

| Rep | Latency (ms) |
|---|---|
| 1 | 23.99 |
| 2 | 21.04 |
| 3 | 21.48 |
| 4 | 20.07 |
| 5 | 17.68 |
| 6 | 17.64 |
| 7 | 17.87 |
| 8 | 19.93 |
| 9 | 18.35 |
| 10 | 17.97 |

**Median = 19.14 ms** · std = 2.00 ms · min = 17.64 ms · max = 23.99 ms

✅ Latency gate PASS (19.14 ms ≤ 25 ms). Узгоджено з Python Dev self-check (17.11 ms).

## False Trigger Rate (T2-6, info-only)

- AWGN buffers tested: 200
- Triggered (conf ≥ 0.4): 4
- Rate: **2.0%**  target ≤5%  ✅ (info-only)

## Висновок

❌ **FAIL** — 3 з 4 блокуючих gate провалені:

- SF accuracy = **~17%** < 85% target → ❌ (баг #1 в `dwt_estimator.py`)
- BW accuracy = **25%** < 80% target → ❌ (баг #2 в `cwt_estimator.py`)
- SF+BW pair = **~5%** < 78% target → ❌ (обидва баги)
- Latency = **19.14 ms** ≤ 25 ms → ✅

**Причина:** Обидва баги системні — реалізація не відповідає специфікації §R2-1/R2-2.
Точність = рівень випадкового вгадування при ВСІХ SNR (від -14 до +6 dB).

→ **Оркестратор НЕ відкриває D2.** Повернути до **Python Dev** (баги #1 та #2 у `src/stage2/`).

Якщо баг #2 стосується помилки специфікації (signal=|IQ| у R2-2) — додатково залучити **DSP Research**.

## Маршрут виправлення

```
Test/QA (FAIL) → Python Dev:
  1. dwt_estimator.py: виправити нормалізацію autocorr_mean
     (замінити mean на |mean| або mean(|autocorr|) або autocorr[0])
  2. cwt_estimator.py: замінити |IQ| на Re(IQ) або inst_freq
     (порадитись з DSP Research щодо spec R2-2)
  → після виправлення → повторний запуск T2-1..T2-7
```

## Артефакти

- `tests/stage2/synth_dataset.py` — T2-1 ✅
- `tests/stage2/test_sf_accuracy.py` — T2-2 (готовий до повторного запуску)
- `tests/stage2/test_bw_accuracy.py` — T2-3 (готовий до повторного запуску)
- `tests/stage2/run_stage2_tests.py` — T2-4..T2-7 runner
- `tests/stage2/test-results-stage2.md` — цей файл
- `obsidian-vault/logs/test-results-stage2-2026-05-29.md` — копія

## Відтворення

```bash
cd /home/tekken/ELRS_Hybrid_Detector_Vault/ELRS_Hybrid_Detector_Vault/tests/stage2
python3 run_stage2_tests.py
```

_Run timestamp: 2026-05-29T00:00:00Z (probe N=10, confirmed with targeted debug)_
