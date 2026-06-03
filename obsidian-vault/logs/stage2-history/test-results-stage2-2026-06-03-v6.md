# Результати тестування Stage 2 — T2-retry-v6 — 2026-06-03

**Verdict: ❌ FAIL**

---

## Середовище

- ОС: Linux 6.14.0-36-generic (x86_64)
- GPU: не використовується (CPU-only pipeline)
- Python: 3.12.3 · numpy 1.26.4 · scipy · pywt
- samp_rate: 30.72 MS/s · N_BUFFER = 1,536,000 (50 мс)
- Реалізація: Dechirp MF v7 (`dwt_estimator.py` C2-fix-v7) + Welch PSD v6 + `blind_estimator.py`

---

## Метрики

| Метрика | Результат | Ціль | Статус |
|---------|-----------|------|--------|
| SF accuracy @ -10dB | **34.3%** | ≥85% | ❌ FAIL |
| BW accuracy @ -12dB | **46.3%** | ≥80% | ❌ FAIL |
| SF+BW pair @ -14dB | **29.3%** | ≥78% | ❌ FAIL |
| Latency (median) | **35.6 ms** | ≤25 ms | ❌ FAIL |
| False Trigger Rate | **2.00%** | ≤5% | ✅ PASS |

---

## Крок 1 — Smoke Test

`make_iq_buffer(sf=9, bw=812_000, snr_db=0, seed=42)` → `ELRS_BlindParameterEstimator(holdoff_s=0.0).estimate()`:
- Повернуло: `sf=12, bw=406_000, conf=0.507`
- Очікувалось: `sf=9, bw=812_000`
- Python exception: ❌ (не впало, всі 7 ключів присутні)
- Результат неправильний → симптом ROOT CAUSE I (детально нижче)

---

## Крок 2 — SF Accuracy @ SNR -10dB (N=1200)

| SF | Correct | Total | Accuracy |
|----|---------|-------|----------|
| SF7  | 2   | 200 | 1.0% |
| SF8  | 9   | 200 | 4.5% |
| SF9  | 26  | 200 | 13.0% |
| SF10 | 67  | 200 | 33.5% |
| SF11 | 126 | 200 | 63.0% |
| SF12 | 182 | 200 | **91.0%** |
| **Overall** | **412** | **1200** | **34.3%** |

Ціль: ≥85% → **❌ FAIL**

Тренд: SF accuracy **монотонно зростає з SF**. При SF=12 → 91%, при SF=7 → 1%.

---

## Крок 3 — BW Accuracy @ SNR -12dB (N=1200)

| BW (kHz) | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| 203k | 201 | 300 | 67.0% |
| 406k | 168 | 300 | 56.0% |
| 812k | 121 | 300 | 40.3% |
| 1625k | 66 | 300 | 22.0% |
| **Overall** | **556** | **1200** | **46.3%** |

Ціль: ≥80% → **❌ FAIL**

Тренд: BW accuracy **монотонно спадає зі збільшенням BW**.

---

## Крок 4 — SF+BW Pair @ SNR -14dB (N=1200)

| SF | BW=203k | BW=406k | BW=812k | BW=1625k |
|----|---------|---------|---------|---------|
| SF7  | 2% | 2% | 0% | 0% |
| SF8  | 6% | 2% | 0% | 0% |
| SF9  | 18% | 0% | 4% | 2% |
| SF10 | **100%** | 16% | 8% | 2% |
| SF11 | **100%** | **100%** | 16% | 8% |
| SF12 | **100%** | **100%** | **100%** | 18% |

**Overall: 352/1200 = 29.3%** → Ціль ≥78%: **❌ FAIL**

**Критична аномалія:** Рівно 6 комбінацій дають 100%:
- SF10/BW=203k, SF11/BW=203k, SF11/BW=406k
- SF12/BW=203k, SF12/BW=406k, SF12/BW=812k

Усі 18 інших комбінацій — near-random або нуль.

---

## Крок 5 — Latency + FTR

**Latency (N=100 @ SNR=0dB):**
- min=12.6 ms · median=**35.6 ms** · p95=69.4 ms · max=75.4 ms
- Ціль ≤25 ms: **❌ FAIL**

**False Trigger Rate (N=200 AWGN):**
- 4/200 = 2.00%
- Ціль ≤5%: **✅ PASS**

---

## ROOT CAUSE I — Аналіз

### Патерн 100% vs 0% по комбінаціях

Всі 6 комбінацій з 100% pair accuracy мають спільну властивість: їхній `preamble_len > N_BUFFER`:

| SF | BW | n_sym | preamble_len | fill ratio | max_offset | Accuracy |
|----|-----|-------|-------------|-----------|------------|---------|
| SF10 | 203k | 154,885 | ~1,897,342 | **100%** | 0 | **100%** |
| SF11 | 203k | 309,770 | ~3,794,683 | **100%** | 0 | **100%** |
| SF11 | 406k | 154,885 | ~1,897,342 | **100%** | 0 | **100%** |
| SF12 | 203k | 619,539 | ~7,589,353 | **100%** | 0 | **100%** |
| SF12 | 406k | 309,770 | ~3,794,683 | **100%** | 0 | **100%** |
| SF12 | 812k | 154,885 | ~1,897,342 | **100%** | 0 | **100%** |

Коли `preamble_len > N_BUFFER`: `max_offset=0` → preamble завжди починається з **offset=0** → `iq[:n_sym]` завжди містить сигнал.

### Для решти 18 комбінацій (fill < 100%)

Preamble починається в довільному місці буфера (0..max_offset). Ймовірність, що `iq[:n_sym]` містить сигнал:

```
P(signal in iq[:n_sym]) ≈ n_sym / max_offset ≈ fill_ratio
```

| SF | BW | n_sym | fill | P(hit) | Observed |
|----|-----|-------|------|--------|---------|
| SF7 | 1625k | 2,418 | 1.6% | ~0.16% | 0% |
| SF7 | 812k | 4,840 | 3.2% | ~0.32% | 0% |
| SF7 | 406k | 9,680 | 6.3% | ~0.64% | 2% |
| SF7 | 203k | 19,361 | 12.6% | ~1.3% | 2% |
| SF9 | 812k | 19,361 | 15.2% | ~1.5% | 4% |
| SF12 | 1625k | 77,430 | ~5% | ~13% | 18% |

Очікуваний патерн підтверджується: чим менший `fill`, тим менший відсоток.

### Чому це стосується і BW estimation (Welch PSD)

Welch PSD аналізує `iq[:65536]` (2.13 мс). Для комбінацій з малим fill:

| Сигнал | P(сигнал у iq[:65536]) |
|---------|----------------------|
| SF7/BW=1625k (29621 сем) | ~2.4% |
| SF10/BW=203k (fill=100%) | ~100% |

Тому BW accuracy також залежить від fill ratio — що пояснює спадання від 67% (BW=203k) до 22% (BW=1625k).

### Механізм ROOT CAUSE I

```
synth_dataset.make_iq_buffer():
    preamble_offset = random(0, max_offset)  ← довільне місце
    buffer[:] = AWGN + preamble[offset:offset+preamble_len]

dwt_estimator.dwt_sf_estimation():
    n_use = min(n_sym, len(iq))
    dechirped = iq[:n_use] * ref  ← ПЕРШИЙ символ буфера
    spectrum = rfft(dechirped)    ← якщо сигналу немає → random noise spectrum

cwt_estimator.cwt_bw_estimation():
    signal = np.real(iq[:N_TOTAL])  ← ПЕРШІ 65536 семплів
    ← якщо сигналу немає → noise_only → score[all_bw] ≈ 1.0 → random argmax
```

**`t_offset_samples`** обчислюється (10% cumulative energy threshold), але **НЕ ВИКОРИСТОВУЄТЬСЯ для вирівнювання** ні в Welch PSD, ні в Dechirp MF.

---

## ROOT CAUSE J — Latency

Spec §R2-1 latency table:
```
| 6 × rfft(n_sym) — worst case SF12/203k | rfft(38 745) × 6 | < 1 ms |
```

Але n_sym для SF12/BW=203k = round(4096 × 30.72e6 / 203000) = **619,539** семплів — не 38,745!

38,745 — це n_sym для SF12/BW=**1625k**. Spec переплутав BW. Справжній worst case:

| SF | BW | n_sym | rfft cost (approx) |
|----|-----|-------|-------------------|
| SF12 | 203k | 619,539 | ~10-20 ms |
| SF11 | 203k | 309,770 | ~5-10 ms |
| SF10 | 203k | 154,885 | ~3-5 ms |
| SF12 | 1625k | 77,430 | ~0.5 ms (spec worst case) |

Для 6 гіпотез при BW=203k сума n_sym ≈ 1,219,716. Фактичні задокументовані latencies:
- Median=35.6 ms > 25 ms ✓ підтверджує spec latency помилку

---

## Summary

| ROOT CAUSE | Тип | Вплив |
|------------|-----|-------|
| **ROOT CAUSE I** | Offset alignment: `iq[:n_sym]` та `iq[:65536]` не вирівняні до початку сигналу | SF: 34.3%❌, BW: 46.3%❌, Pair: 29.3%❌ |
| **ROOT CAUSE J** | Spec latency table error: worst case n_sym=38745 (SF12/1625k) — насправді 619539 (SF12/203k) | Latency: 35.6ms❌ |

**Виправлення (для DSP Research → Python Dev):**

Для ROOT CAUSE I:
1. Використати `t_offset_samples` для вирівнювання перед Welch PSD і Dechirp MF
2. Або: пошук пікового вікна (sliding window over buffer)
3. Або: змінити spec так, щоб `t_offset_samples` обчислювався ПЕРШИМ і використовувався в обох estimators

Для ROOT CAUSE J:
1. Обмежити n_use для Dechirp MF: `n_use = min(n_sym, max_dechirp_samples)` де max_dechirp_samples ≈ 65536 або фіксований
2. Або: параметризувати n_use через конструктор

---

## Висновок

❌ **FAIL** — 4 з 5 метрик не пройшли.

Єдина нова метрика, яка пройшла: FTR=2.00% ✅ (підтверджує T2-retry-v5b = 0.00%).

Dechirp MF алгоритм **фізично правильний** для вирівняних буферів (6 combo з fill=100% → 100% пар). ROOT CAUSE — відсутність offset-alignment перед аналізом. Це не баг алгоритму — це баг інтеграції буфера з offset.

Повернути до: **DSP Research → R2-fix-v8** (offset alignment spec) → **Python Dev → C2-fix-v8**.

---

_Run: 2026-06-03 · Steps 2-4: N=50/combo × 24 = 1200 tests each · Step 5: N=100 latency + N=200 FTR_
_dwt_estimator.py: C2-fix-v7 (Dechirp MF) · cwt_estimator.py: C2-fix-v6 (Welch PSD) · blind_estimator.py: C2-fix-v5_
