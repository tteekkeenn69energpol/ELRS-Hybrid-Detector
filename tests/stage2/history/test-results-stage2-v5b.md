# Результати тестування Stage 2 — T2-retry-v5b (spec v6 / C2-fix-v6, corrected briefing) — 2026-06-02

**Verdict: ❌ FAIL**

> T2-retry-v5b: тестування після двох виправлень у брифінгу Оркестратора:
> (1) `f1=bw_hz/2` у `make_css_chirp` (замість `f1=bw_hz`);
> (2) Крок 1 @ SNR=+6dB (замість clean chirp).
> Базові лінії: T2-retry-v4 FAIL (ROOT CAUSE F), T2-retry-v5 FAIL (ROOT CAUSE G-1/G-2).

---

## Середовище

- ОС: `Linux-6.14.0-36-generic-x86_64-with-glibc2.39`
- Host: `tekken-Latitude-5580`
- CPU: `13th Gen Intel(R) Core(TM) i5-13600KF` (20 cores)
- Python: `3.12.3` (numpy 1.26.4, pywt, scipy)
- samp_rate: 30.72 MS/s · buffer: 50 ms = 1,536,000 samples
- BW: Welch PSD (N_total=65536, N_fft=4096, K=31, Hann, per-class hypothesis, noise_freq_min=3.25MHz)
- DWT: Re(IQ), sym5/L4, bw_candidate від PSD, single-column search
- Сигнал: `make_css_chirp` — real chirp f0=0 → f1=BW/2, 12 символів + zero-pad до 1.5M, AWGN

---

## Ключові метрики (gate)

| Метрика | Результат | Ціль | |
|---|---|---|---|
| SF accuracy @ SNR≥-10dB | **20.8%** | ≥85% | ❌ |
| BW accuracy @ SNR≥-12dB | **87.5%** | ≥80% | ✅ |
| SF+BW pair @ SNR=-14dB  | **18.2%** | ≥78% | ❌ |
| Latency (100 reps, median) | **12.30ms** | ≤25ms | ✅ |
| False trigger rate (10000 AWGN) | **0.00%** | ≤5% | ✅ |

**2 блокуючих метрики не пройдені: SF accuracy та SF+BW pair.**

---

## Деталізація результатів

### Крок 2 — SF accuracy @ SNR=-10dB (24×500=12,000 tests) [399s]

| SF | Correct | Total | Accuracy |
|----|---------|-------|----------|
| SF7  | 665  | 2000 | 33.2% |
| SF8  | 400  | 2000 | 20.0% |
| SF9  | 761  | 2000 | 38.0% |
| SF10 | 253  | 2000 | 12.7% |
| SF11 | 242  | 2000 | 12.1% |
| SF12 | 179  | 2000 |  8.9% |
| **Overall** | **2500** | **12000** | **20.8%** ❌ |

### Крок 3 — BW accuracy @ SNR=-12dB (24×500=12,000 tests) [377s]

| BW | Correct | Total | Accuracy |
|----|---------|-------|----------|
| 203k  | 3000 | 3000 | 100.0% |
| 406k  | 2000 | 3000 |  66.7% |
| 812k  | 2500 | 3000 |  83.3% |
| 1625k | 3000 | 3000 | 100.0% |
| **Overall** | **10500** | **12000** | **87.5%** ✅ |

BW prediction distribution: {203k:4000, 406k:2500, 812k:2500, 1625k:3000}
method='psd+dwt' ✓

### Крок 4 — SF+BW pair @ SNR=-14dB (24×500=12,000 tests) [377s]

| Метрика | Результат |
|---------|-----------|
| Correct pairs | 2179 / 12000 |
| **Pair accuracy** | **18.2%** ❌ |

### Крок 5a — Latency (100 reps, SF=9/BW=812k @ -6dB)

| Метрика | Значення |
|---------|---------|
| Median  | **12.30 ms** ✅ |
| p95     | 13.58 ms |
| Mean    | 12.55 ms |

Welch PSD (65536 samples) ≈ 2ms · DWT (1.5M samples) ≈ 10ms · Total ≈ 12ms ✓

### Крок 5b — FTR (10,000 pure AWGN buffers)

| Метрика | Значення |
|---------|---------|
| Triggered | 0 / 10000 |
| **FTR** | **0.00%** ✅ |

Confidence gate (threshold_low=0.4) відхиляє AWGN безвідмовно ✓

---

## ROOT CAUSE H — DWT SF estimation fails

### Спостереження

DWT SF accuracy = **20.8%** при цілі ≥85%. Жодне значення SF не досягає 40%.
BW accuracy при цьому = **87.5%** — Welch PSD BW estimator (C2-fix-v6) **працює коректно**.

### Аналіз fill ratio по (SF, BW)

`make_css_chirp` генерує рівно 12 символів і zero-pad до N_BUFFER=1,536,000:

```
signal_samples = round(2^SF / BW_hz × 30.72e6) × 12
```

| SF | BW=203k | BW=406k | BW=812k | BW=1625k |
|----|---------|---------|---------|---------|
| SF7  | 15.1% | 7.6%  | 3.8% | 1.9% |
| SF8  | 30.2% | 15.1% | 7.6% | 3.8% |
| SF9  | 60.5% | 30.2% | 15.1%| 7.6% |
| SF10 | 100%  | 60.5% | 30.2%| 15.1%|
| SF11 | 100%  | 100%  | 60.5%| 30.2%|
| SF12 | 100%  | 100%  | 100% | 60.5%|

**Критичне спостереження:** SF12 з BW=203k/406k/812k має fill=100% (signal > N_BUFFER → обрізається),
але SF12 accuracy = **8.9%** — найгірший з усіх. Zero-padding **не є** єдиним root cause.

### Гіпотези ROOT CAUSE H

**H-1 (часткова): Zero-padding для малого SF × великого BW**

Для SF7/BW=1625k: 29,040 сигнальних семплів у буфері 1,536,000 (1.9%).
DWT detail коефіцієнти Level-4 (cD_4): 1,536,000/16 = 96,000 елементів,
з яких лише 29,040/16 = 1,815 несуть сигнал → autocorr peak послаблюється ~52×.
Пояснює низьку точність для SF7–SF9 з великими BW.
**Але не пояснює SF12 failures (fill=100%).**

**H-2 (імовірна): Signal model mismatch — real chirp f0=0→f1=BW/2**

DWT pre-screen очікує wrap-around bursts в `Re(IQ)` при CSS символьних межах.
`make_css_chirp` генерує: `sp_chirp(t, f0=0, f1=BW/2, method='linear')` — реальний
косинусний чирп від 0 Гц до BW/2.

Проблема: у справжньому ELRS CSS (комплексний IQ, baseband) чирп має спектральну
симетрію і wrap-around від BW/2 → -BW/2. Реальний чирп f0=0 → f1=BW/2 має
wrap-around: в момент перезапуску символу частота стрибає з BW/2 назад до 0 Hz
(різка зміна IF). DWT L4 може не захоплювати цей transient при всіх (SF, BW)
конфігураціях, якщо scale sym5 не оптимізований під f0=0.

**H-3 (можлива): DWT lag table або autocorr logic bug**

`_LAG_TABLE` і autocorr windowing потребують перевірки незалежно від сигналу.
Якщо expected_lag поза реальним піком → 0 hits незалежно від fill.

### Висновок по ROOT CAUSE H

Точна причина не локалізована до одного компонента. Найімовірніша комбінація:
- **H-1** пояснює деградацію при малих fill (SF7-SF9, великий BW)
- **H-2** пояснює провал навіть при fill=100% (SF12)

**Дії: Повернути до DSP Research (R2-fix-dwt) для:**

1. Перевірки `_LAG_TABLE` та autocorr windowing незалежно від test signal
2. Перевірки wrap-around burst структури для real chirp f0=0→f1=BW/2
3. Якщо signal model H-2: скорегувати алгоритм або специфікацію сигналу

---

## Прогрес по версіях (SF/BW accuracy)

| Компонент | v1–v4 | v5 | **v5b** |
|---|---|---|---|
| BW accuracy | 25% (random) | 25% (all→1625k) | **87.5%** ✅ |
| SF accuracy | ~15% | 16.1% | **20.8%** ❌ |
| Latency | 12–79ms | 12ms ✅ | **12.30ms** ✅ |
| FTR | 0–2% | 0% ✅ | **0.00%** ✅ |

**BW — вперше вийшла з random baseline.** SF — досі не досягає цілі.

---

## Підсумок

❌ **FAIL** — 2 блокуючих метрики:

| Метрика | Результат | Ціль | |
|---|---|---|---|
| SF accuracy @ -10dB | **20.8%** | ≥85% | ❌ |
| BW accuracy @ -12dB | **87.5%** | ≥80% | ✅ |
| pair @ -14dB | **18.2%** | ≥78% | ❌ |
| Latency | **12.30ms** | ≤25ms | ✅ |
| FTR | **0.00%** | ≤5% | ✅ |

**ROOT CAUSE H:** DWT SF estimation не досягає цілі. Точний механізм потребує
діагностики DSP Research: zero-padding (H-1) та/або signal model mismatch (H-2).
Welch PSD BW estimator (C2-fix-v6) — **підтверджений як робочий** (87.5% ✅).

**D2 заблоковано. Повернути до Оркестратора → DSP Research → R2-fix-dwt.**

---

_Run: 2026-06-02 · N=500/combo · Steps 2-4 (12,000 tests each) · Latency 100 reps · FTR 10,000 AWGN_
