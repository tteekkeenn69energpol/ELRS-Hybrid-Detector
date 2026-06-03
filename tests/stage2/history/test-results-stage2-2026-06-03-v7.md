# Результати тестування Stage 2 — T2-retry-v7 — 2026-06-03

**Verdict: ❌ FAIL**

---

## Середовище

- ОС: Linux 6.14.0-36-generic
- Python: 3.12.3 · numpy 1.26.4 · scipy
- samp_rate: 30.72 MS/s · N_BUFFER = 1,536,000 (50 мс)
- Реалізація: Dechirp MF v8 (`dwt_estimator.py` C2-fix-v8) + Welch PSD v6 + `blind_estimator.py` C2-fix-v8
- t_offset: реальний (rng state save/restore з synth_dataset._build_preamble)

---

## Метрики

| Метрика | v6 (без t_offset) | v7 (реальний t_offset) | Ціль | Статус |
|---------|-------------------|----------------------|------|--------|
| SF accuracy @ -10dB | 34.3% | **46.8%** | ≥85% | ❌ FAIL |
| BW accuracy @ -12dB | 46.3% | **46.3%** | ≥80% | ❌ FAIL |
| SF+BW pair @ -14dB | 29.3% | **46.3%** | ≥78% | ❌ FAIL |
| Latency median | 35.6 ms | **30.5 ms** | ≤25 ms | ❌ FAIL |
| FTR | 2.00% | **2.00%** | ≤5% | ✅ PASS |

---

## Крок 1 — Smoke Test

`make_iq_buffer(sf=9, bw=812k, snr_db=0, seed=42)` → t_offset=115911, `estimate(buf, t_offset=115911)`:
- Повернуло: `sf=7, bw=406000` ← wrong
- Python exception: ❌ не впало
- Причина: bw_candidate від Welch PSD неправильний (ROOT CAUSE K — пояснення нижче)

---

## Крок 2 — SF Accuracy @ SNR -10dB (N=1200)

| SF | Correct | Total | Accuracy |
|----|---------|-------|----------|
| SF7  | 58  | 200 | 29.0% |
| SF8  | 54  | 200 | 27.0% |
| SF9  | 64  | 200 | 32.0% |
| SF10 | 89  | 200 | 44.5% |
| SF11 | 132 | 200 | 66.0% |
| SF12 | 164 | 200 | 82.0% |
| **Overall** | **561** | **1200** | **46.8%** |

Ціль ≥85% → **❌ FAIL**

**Порівняння з v6:** SF7: 1%→29%, SF8: 4.5%→27%, SF9: 13%→32% — t_offset помітно допоміг.
Але загальний результат обмежений BW accuracy (46.3%) — якщо bw_candidate хибний, Dechirp дає хибний SF.

---

## Крок 3 — BW Accuracy @ SNR -12dB (N=1200)

| BW (kHz) | Correct | Total | v6 | v7 |
|----------|---------|-------|-----|-----|
| 203k | 201 | 300 | 67.0% | **67.0%** |
| 406k | 168 | 300 | 56.0% | **56.0%** |
| 812k | 121 | 300 | 40.3% | **40.3%** |
| 1625k | 66 | 300 | 22.0% | **22.0%** |
| **Overall** | **556** | **1200** | **46.3%** | **46.3%** |

Ціль ≥80% → **❌ FAIL**

**Ключова спостереження: BW accuracy = ІДЕНТИЧНА v6 (до 0.1%).**
`cwt_estimator.py` не змінювався в C2-fix-v8 → Welch PSD завжди аналізує `iq[:65536]` незалежно від t_offset.

---

## Крок 4 — SF+BW Pair @ SNR -14dB (N=1200)

| SF | BW=203k | BW=406k | BW=812k | BW=1625k |
|----|---------|---------|---------|---------|
| SF7  | 40% | 30% | 22% | 20% |
| SF8  | 38% | 32% | 34% | 16% |
| SF9  | 40% | 26% | 32% | 22% |
| SF10 | **100%** | 48% | 20% | 20% |
| SF11 | **100%** | **100%** | 26% | 20% |
| SF12 | **100%** | **100%** | **100%** | 26% |

**Overall: 556/1200 = 46.3%** → Ціль ≥78%: **❌ FAIL**

**Покращення від v6:** Non-fill-100% комбо: 0-18% → 16-48%. t_offset реально допоміг SF detection. Але BW estimation ще неправильний для малих fill → пара не збігається.

Значущо: fill=100% combos (SF10+/BW≤812k) = 100% пар точність ✓

---

## Крок 5 — Latency + FTR

**Latency (N=100 @ 0dB):**
- min=12.5ms · median=**30.5ms** · p95=57.6ms · max=60.5ms
- SF12/203k worst case: 30.3–30.9ms (median 30.8ms)
- Ціль ≤25ms: **❌ FAIL**

**FTR (N=200 AWGN, t_offset=0):**
- 4/200 = 2.00% ✅

---

## ROOT CAUSE K — Welch PSD не використовує t_offset

### Механізм

```
cwt_estimator.cwt_bw_estimation():
    signal = np.real(iq_np[:_N_TOTAL]).astype(np.float64)
    #                       ^^^^^^^^ завжди перші 65,536 семплів
    # t_offset НЕ є параметром cwt_bw_estimation
    # blind_estimator.py НЕ передає t_offset до cwt_bw_estimation
```

`C2-fix-v8` оновив лише `dwt_estimator.py` (+ `blind_estimator.py` для передачі t_offset у dwt_sf_estimation). `cwt_estimator.py` залишився незмінним.

### Доказ: BW accuracy тотожна v6

BW accuracy v6 = 46.3% / BW accuracy v7 = 46.3% — різниця 0.0%.
Тест v7 використовує реальний t_offset, але BW залежить від Welch PSD, яка його ігнорує.

### Вплив на SF+BW pair

Pipeline: `Welch PSD → bw_candidate → Dechirp MF(bw_candidate, t_offset)`.
Якщо bw_candidate хибний → Dechirp шукає не той SF → pair неправильна навіть з реальним t_offset.

### P(signal in iq[:65536]) за BW

| BW | preamble_len (SF7) | max_offset | P(overlap) | Observed BW acc |
|----|-------------------|------------|------------|-----------------|
| 203k | 237,173 | 1,298,827 | 5.0% (partial) → eff. ~45% | 67.0% |
| 406k | 118,587 | 1,417,413 | 4.6% (partial) → eff. ~38% | 56.0% |
| 812k | 59,293 | 1,476,707 | 4.4% (partial) → eff. ~28% | 40.3% |
| 1625k | 29,621 | 1,506,379 | 4.3% (partial) → eff. ~15% | 22.0% |

(eff. = враховує avg overlap length та high local SNR — велика преамбула краще перекриває вікно)

### Виправлення

`cwt_estimator.cwt_bw_estimation(iq, ..., t_offset=0)` + `signal = np.real(iq_np[t_offset:t_offset+_N_TOTAL])`.
`blind_estimator.estimate()` передає t_offset у cwt_bw_estimation.
Потребує: **R2-fix-v9** (§R2-2: додати t_offset) + **C2-fix-v9** (cwt_estimator.py + blind_estimator.py).

---

## ROOT CAUSE L — FFT з n=n_sym замість n=n_use

### Механізм

```python
# dwt_estimator.py — поточний код:
n_use = min(n_sym, _N_DECHIRP_MAX, n_total - t_offset)   # ≤ 65536
dechirped = iq_arr[t_offset : t_offset + n_use] * ref    # n_use семплів
spectrum = np.abs(sp_fft(dechirped, n=n_sym)) ** 2       # FFT з n=n_sym ← ПРОБЛЕМА
```

`sp_fft(array_of_65536_samples, n=619539)` — нуль-доповнює до 619,539 і обчислює FFT розміром 619,539. Це операція O(n_sym × log(n_sym)), де n_sym може бути 619,539.

### Виміряна затримка

| Combo | n_sym | n_use | FFT size | Measured |
|-------|-------|-------|----------|----------|
| SF12/BW=203k | 619,539 | 65,536 | 619,539 | **30.8 ms** |
| SF12/BW=406k | 309,770 | 65,536 | 309,770 | ~15 ms |
| SF12/BW=812k | 154,885 | 65,536 | 154,885 | ~8 ms |
| SF7/BW=1625k | 2,418 | 2,418 | 2,418 | < 1 ms |

Медіана 30.5ms > 25ms через циклічне чергування SF12/BW=203k у latency тесті.

### Чому FFT(n_use) підходить

Для правильної гіпотези SF: dechirped = DC тон + noise.
- `sp_fft(n=n_use)`: score = n_use × SNR = 65536 × 0.1 = 6554 @ -10dB >> noise (2-4)
- `sp_fft(n=n_sym)`: score ≈ n_use × n_sym/n_use × SNR = n_sym × SNR = 619539 × 0.1 = 61954

Обидва варіанти мають огромний margin. argmax = однаковий SF. Виправлення:
`spectrum = np.abs(sp_fft(dechirped, n=n_use)) ** 2` — FFT(65536) ≈ 0.3ms, vs FFT(619539) ≈ 30ms.

Потребує: **C2-fix-v9** (dwt_estimator.py: `n=n_use` замість `n=n_sym`).

---

## Порівняльна таблиця

| Версія | ROOT CAUSE | SF% | BW% | Pair% | Latency |
|--------|-----------|-----|-----|-------|---------|
| v5b (DWT autocorr) | H: DWT cD_4 fails | 20.8% | 87.5% | 18.2% | 12.3ms |
| v6 (Dechirp, no offset) | I: iq[:n_sym] random placement | 34.3% | 46.3% | 29.3% | 35.6ms |
| v7 (Dechirp, t_offset) | K: BW uses iq[:65k], L: FFT n=n_sym | 46.8% | 46.3% | 46.3% | 30.5ms |

---

## Висновок

❌ **FAIL** — 4 з 5 метрик не пройшли.

**Прогрес:** Dechirp MF алгоритм корректний (fill=100% combo → 100% pair). t_offset патч покращив SF і pair accuracy на 12-17%. Але дві залишкові проблеми у spec:

1. **ROOT CAUSE K**: `cwt_estimator.py` потребує `t_offset` параметра — §R2-2 spec не специфікував його.
2. **ROOT CAUSE L**: `dwt_estimator.py` використовує `n=n_sym` для FFT — §R2-1 spec сказав `n=n_sym`, але правильно `n=n_use`.

Повернути до: **DSP Research → R2-fix-v9** (§R2-2 t_offset + §R2-1 n=n_use) → **Python Dev → C2-fix-v9**.

---

_Run: 2026-06-03 · Steps 2-4: N=50/combo × 24 = 1200 tests each · Step 5: N=100 latency + N=200 FTR_
_t_offset: rng state save/restore з synth_dataset._build_preamble_
