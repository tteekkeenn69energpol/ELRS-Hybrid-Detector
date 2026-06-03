# Діагностичний звіт — T2-retry-v5c — ROOT CAUSE H ізоляція — 2026-06-02

**Verdict: H-2 ПІДТВЕРДЖЕНО** — баг у `dwt_estimator.py`, не у тест-генераторі.

---

## Задача

Ізолювати ROOT CAUSE H-1 від H-2:
- **H-1**: `make_css_chirp` n_sym=12 → мала fill ratio → DWT не бачить символьну periodicity
- **H-2**: `dwt_estimator.py` не знаходить SF навіть при правильному сигналі

---

## Середовище

- Python 3.12.3 · numpy 1.26.4 · pywt · scipy
- samp_rate: 30.72 MS/s · N_BUFFER=1,536,000 (50ms)
- DWT: `dwt_sf_estimation(iq, bw_candidate=true_bw)` — ПРЯМЕ звернення, без blind_estimator
- SNR: -10dB (критичний поріг для SF accuracy gate)

---

## ВИМІР A — synth_dataset.py → dwt_sf_estimation напряму (N=50/combo, 1200 тестів)

**Умови:** `make_iq_buffer(sf, bw, snr_db=-10)` + `dwt_sf_estimation(iq, bw_candidate=bw_true)`
(bw_candidate = СПРАВЖНІЙ BW, не estimated — усуває BW-помилки з рівняння)

### Per-SF результати

| SF | Correct | Total | Accuracy | Predictions distribution |
|----|---------|-------|----------|--------------------------|
| SF7  | 76  | 200 | 38.0% | SF7:76, SF8:27, SF9:26, SF10:22, SF11:28, SF12:21 |
| SF8  | 30  | 200 | 15.0% | SF7:25, SF8:30, SF9:67, SF10:28, SF11:28, SF12:22 |
| SF9  | 75  | 200 | 37.5% | SF7:25, SF8:23, SF9:75, SF10:22, SF11:28, SF12:27 |
| SF10 | 34  | 200 | 17.0% | SF7:46, SF8:50, SF9:32, SF10:34, SF11:20, SF12:18 |
| SF11 | 28  | 200 | 14.0% | SF7:44, SF8:38, SF9:42, SF10:36, SF11:28, SF12:12 |
| SF12 | 32  | 200 | 16.0% | SF7:41, SF8:22, SF9:40, SF10:28, SF11:37, SF12:32 |
| **Overall** | **275** | **1200** | **22.9%** | |

**Random baseline: 1/6 = 16.7%. Observed: 22.9% ≈ near-random.**

### Висновок по Виміру A

**22.9% < 50% → H-2 ПІДТВЕРДЖЕНО.** DWT не знаходить SF навіть при:
- Канонічному сигналі (`synth_dataset.py` — офіційний генератор)
- Правильному bw_candidate (справжній BW)
- SNR = -10 dB

---

## ВИМІР B — SF12/BW=812k: synth_dataset vs make_css_chirp (N=100 кожен)

| Генератор | Correct | Total | Accuracy | Predictions distribution |
|-----------|---------|-------|----------|--------------------------|
| `synth_dataset.py` | 14 | 100 | **14.0%** | {7:18, 8:16, 9:23, 10:20, 11:9, 12:14} |
| `make_css_chirp` (f1=BW/2) | 18 | 100 | **18.0%** | {7:22, 8:15, 9:19, 10:16, 11:10, 12:18} |

**Обидва генератори дають майже ідентичні (random) результати:**
- synth: 14.0% vs css: 18.0% — різниця 4% (в межах статистичного шуму)
- Обидва ≈ random baseline (1/6 = 16.7%)

### Висновок по Виміру B

**H-2 підтверджено:** `make_css_chirp` vs `synth_dataset.py` не має суттєвої різниці.
DWT однаково провалюється для обох генераторів при SF12/BW=812k.

---

## ДЕТАЛЬНА РОЗБИВКА per (SF, BW) — Вимір A

(f=fill ratio прогнозований для make_css_chirp; synth використовує random offset але ~однаковий fill)

| SF  | BW=203k | BW=406k | BW=812k | BW=1625k |
|-----|---------|---------|---------|---------|
| SF7  | 8/50=**16%** (f15%) | 5/50=**10%** (f8%) | 13/50=**26%** (f4%) | **50/50=100%** (f2%) |
| SF8  | 13/50=**26%** (f31%) | 10/50=**20%** (f15%) | 7/50=**14%** (f8%) | **0/50=0%** (f4%) |
| SF9  | 8/50=**16%** (f62%) | 8/50=**16%** (f31%) | 9/50=**18%** (f15%) | **50/50=100%** (f8%) |
| SF10 | 16/50=**32%** (f100%) | 7/50=**14%** (f62%) | 11/50=**22%** (f31%) | **0/50=0%** (f15%) |
| SF11 | 9/50=**18%** (f100%) | 5/50=**10%** (f100%) | 14/50=**28%** (f62%) | **0/50=0%** (f31%) |
| SF12 | 6/50=**12%** (f100%) | 15/50=**30%** (f100%) | 11/50=**22%** (f100%) | **0/50=0%** (f62%) |

### Критична аномалія: BW=1625k колонка

- **SF7/BW=1625k: 100% (50/50)** і **SF9/BW=1625k: 100% (50/50)** — системно perfect
- **SF8,SF10,SF11,SF12/BW=1625k: 0%** — системно повний провал

Лаги у _LAG_TABLE для BW=1625k:
- SF7: 151, SF8: 302, SF9: 605, SF10: 1209, SF11: 2419, SF12: 4838

**Підозра — помилки у lag table для BW=1625k (SF10–SF12):**

Незалежна перевірка формули `lag = round(2^SF × samp_rate / (BW × 2^level))`:

| SF | N_sym (розраховано) | True lag (round(N_sym/16)) | Table lag | Delta |
|----|--------------------|-----------------------------|-----------|-------|
| SF7  | round(128×30.72e6/1625k) = 2420 | round(2420/16) = **151** | 151 | **0** ✓ |
| SF8  | round(256×30.72e6/1625k) = 4839 | round(4839/16) = **302.4 → 302** | 302 | **0** ✓ |
| SF9  | round(512×30.72e6/1625k) = 9679 | round(9679/16) = **604.9 → 605** | 605 | **0** ✓ |
| SF10 | round(1024×30.72e6/1625k) = 19358 | round(19358/16) = **1209.9 → 1210** | **1209** | **-1 ✗** |
| SF11 | round(2048×30.72e6/1625k) = 38717 | round(38717/16) = **2419.8 → 2420** | **2419** | **-1 ✗** |
| SF12 | round(4096×30.72e6/1625k) = 77433 | round(77433/16) = **4839.6 → 4840** | **4838** | **-2 ✗** |

**Lag table errors: SF10 off by 1, SF11 off by 1, SF12 off by 2 для BW=1625k.**

Це пояснює 0% для SF10/SF11/SF12/BW=1625k: алгоритм шукає пік у неправильному lag.

**Але NOT SUFFICIENT для загального висновку:** SF7/SF9/BW=1625k мають правильні лаги і дають 100%, але решта 18 з 24 комбінацій (включаючи SF12/BW=203k з fill=100% і правильним лагом) дають near-random (~10-30%). Lag table errors — ВТОРИННА проблема, фундаментальний DWT провал — первинна.

---

## ROOT CAUSE H — Уточнена діагностика

### H-1 (тест-генератор): СПРОСТОВАНО як основна причина

- `synth_dataset.py` з fill від 1.9% до 100% → однаково near-random
- SF12/BW=203k (fill=100%) → лише 12% accuracy
- `make_css_chirp` vs `synth_dataset.py` → різниця ≤4% (статистичний шум)

Fill ratio НЕ є детермінуючим фактором.

### H-2 (DWT алгоритм): ПІДТВЕРДЖЕНО

DWT autocorrelation не детектує SF навіть при:
- Правильному сигналі (synth_dataset.py canonical format)
- Правильному bw_candidate
- SNR = -10 dB
- Повному заповненні буфера (fill=100%)

**Можливі механізми (для DSP Research Investigation):**

**H-2a: Wrap-around transient слабкий у Re(IQ)**
`synth_dataset.py` генерує комплексний IQ `exp(j×phase)` з f0=-BW/2→+BW/2.
`Re(IQ) = cos(phase)`. На символьних межах (UP→UP): phase=0 → cos=1, d(cos)/dt=0, d²(cos)/dt²=-(π×BW)² → ОДНАКОВО ДО і ПІСЛЯ межі. Перша і друга похідні Re(IQ) неперервні при UP→UP переходах.
Тільки UP→SYNC та SYNC→DOWN межі мають дійсний розрив у Re(IQ) (2 з 12+ меж).
→ cD_4 має енергетичні сплески тільки у 2 точках preamble (не у 12), autocorr peak слабкий.

**H-2b: Lag table помилки (підтверджено для BW=1625k SF10-SF12)**
_LAG_TABLE: SF10/1625k=1209 (має бути 1210), SF11/1625k=2419 (→2420), SF12/1625k=4838 (→4840).
Аналогічні похибки можуть існувати для інших BW. Потрібна повна ревізія таблиці.

**H-2c: Autocorr normalization range bias**
`lag_max = min(len(autocorr)-1, max(all_lags)*2)` = min(95999, 77490) = 77490.
При sparse preamble (fill<10%): mean(|autocorr[75:77490]|) dominated by near-zero lags
→ arbitrary argmax over the 6 candidates (no true peak stands out consistently).
При full fill (fill=100%): AWGN autocorr dominates normalization → peak drowned in noise floor.

### Вторинна аномалія: SF7/BW=1625k і SF9/BW=1625k = 100%

Обидва мають правильні лаги (151, 605) у таблиці.
Можливе пояснення: для цих малих лагів (маленькі SF, великий BW → короткий символ) autocorr[lag] отримує більше contributing pairs в межах preamble region (lag << N_preamble/16) → випадково домінує над іншими кандидатами. Потребує підтвердження DSP Research.

---

## Таблиця інтерпретації (з брифінгу)

| Умова | Висновок |
|-------|---------|
| Вимір A ≥85% | H-1 → T2-retry-v5d з synth |
| Вимір A <50%, synth >> css | H-1 частково |
| **Вимір A <50%, обидва низькі** | **→ H-2 ПІДТВЕРДЖЕНО ✓** |

**Вимір A = 22.9% < 50%** ✓
**synth = 14% ≈ css = 18%** ✓

**→ H-2 ПІДТВЕРДЖЕНО. Потрібна R2-fix-v7 від DSP Research.**

---

## Summary

| | Вимір A | Вимір B |
|---|---|---|
| Signal | synth_dataset.py | synth=14%, css=18% |
| SF overall | **22.9%** | SF12/BW=812k both fail |
| Random baseline | 16.7% | 16.7% |
| Difference from random | +6.2% | +1.3% / +1.3% |
| **Conclusion** | **H-2** | **H-2** |

**H-1 спростовано. H-2 підтверджено.**

Другорядні знахідки для DSP Research:
1. Lag table errors підтверджено для BW=1625k, SF10-SF12 (off by 1-2)
2. Re(IQ) wrap-around transients присутні лише на UP→SYNC та SYNC→DOWN межах (2/12+)
3. SF7/BW=1625k і SF9/BW=1625k дають 100% — аномалія потребує дослідження

---

_Run: 2026-06-02 · Вимір A: N=50/combo × 24 = 1200 tests · Вимір B: N=100 кожен [62s total]_
