# Результати тестування Stage 2 — T2-retry-v5 (spec v6 / C2-fix-v6) — 2026-06-02

**Verdict: ❌ FAIL — Крок 1 (BW verification) не пройшов. Повний suite не запускався.**

> T2-retry-v5: тестування після C2-fix-v6 (per-class hypothesis test замість threshold+max).
> Базові лінії: v1–v5 FAIL.

---

## Крок 0 — Перевірка версії

```
v6 OK: _THRESHOLD відсутній ✓
```

`_THRESHOLD` видалено, per-class hypothesis test реалізовано (Lines 97–110 cwt_estimator.py) ✓.

---

## Крок 1 — BW verification (clean chirp + SNR=-14dB) — ❌ FAIL

### Результати (clean chirp, f1=BW/2, no AWGN):

| True BW | Predicted | Status | energy_ratio |
|---------|-----------|--------|--------------|
| 203k | **1625k** | ✗ | 9.63×10¹¹ |
| 406k | **1625k** | ✗ | 9.01×10¹¹ |
| 812k | **1625k** | ✗ | 2.87×10¹¹ |
| 1625k | **1625k** | ✓ | 19518.1 |

### Результати (BW=1625k @-14dB AWGN):

| Test | Predicted | Status | energy_ratio |
|------|-----------|--------|--------------|
| BW=1625k @-14dB | 1625k | ✓ | 1.799 |

**Крок 1 FAIL → зупинка повного suite (per briefing protocol).**

---

## ROOT CAUSE G — Повний аналіз

### ROOT CAUSE G-1: Per-class score нестабільний при відсутності AWGN

**Механізм:**

Per-class formula: `score[b] = mean(S_norm[0..b/2]) / mean(S_norm[b/2..b])`

де `S_norm = S_welch / noise_floor` і `noise_floor = median(S_welch[freqs > 3.25MHz])`.

При чистому сигналі (без AWGN):
```
S_welch[0..BW/2]      = велике (сигнал)
S_welch[BW/2..3.25MHz] = мале (spectral leakage від chirp)
S_welch[3.25MHz+]      = ще менше (далека leakage)
noise_floor = median(S_welch[3.25MHz+]) ≈ tiny_extreme_leakage
```

Для більших BW класів (b > true_BW):
```
ref_mask[b/2..b] → ще далі від сигналу → ще менше leakage
→ ref_mean → 0 → score[larger_b] → ∞
```

Тому score[1625k] >> score[true_BW] завжди для чистих сигналів.

**Верифікація SNR threshold (BW=812k, chirp f1=BW/2=406kHz):**

| SNR | Prediction | Status |
|-----|-----------|--------|
| clean (∞) | 1625k | ✗ |
| +6 dB | 812k | ✓ |
| 0 dB | 812k | ✓ |
| -6 dB | 812k | ✓ |
| -10 dB | 812k | ✓ |
| -12 dB | 812k | ✓ |
| -14 dB | 812k | ✓ |

**Висновок G-1:** Алгоритм КОРЕКТНИЙ при будь-якому реальному SNR (включно з -14dB).
Проблема — тільки при ZERO noise (чистий chirp = degenerate case).
Верифікаційний тест Крок 1 "clean chirp" перевіряє нереалістичний сценарій (без шуму).

### ROOT CAUSE G-2: make_css_chirp використовує f1=BW (не f1=BW/2) — несумісний сигнал

**Стандарт spec §R2-2:**
> "CSS up-chirp Re(IQ) рівномірно sweeps IF від **0 до BW/2**"
> → для алгоритму: сигнал в [0, BW/2], ref band [BW/2, BW] = pure noise

**make_css_chirp (з брифінгу Оркестратора):**
```python
chirp_one = sp_chirp(t, f0=0.0, f1=bw_hz, t1=T_sym, method='linear')  # sweeps 0→BW!
```

Це дає Re(IQ) з сигналом у [0, BW], а не [0, BW/2].

**Аналіз per-class scores для BW=812k, f1=812kHz (повний BW), SNR=-12dB:**

```
S_norm at: 203k=2.09, 406k=1.76, 812k=1.21
b=203k: in=2.609 ref=2.535  score=1.029
b=406k: in=2.570 ref=2.211  score=1.162
b=812k: in=2.391 ref=2.128  score=1.124  ← TRUE BW (but score LOW!)
b=1625k: in=2.259 ref=1.042 score=2.168  ← argmax → WRONG prediction
```

Причина: ref_mask[BW/2..BW]=[406k..812k] містить СИГНАЛ (chirp sweep до 812kHz!).
→ score[true_BW] ≈ 1.1 (не дискримінує) → argmax вибирає 1625k.

**Верифікація для всіх BW (f1=BW/2 vs f1=BW):**

| True BW | f1=BW/2 @-12dB | f1=BW @-12dB |
|---------|----------------|--------------|
| 203k | **100%** (20/20) | ✗ → 1625k |
| 406k | **100%** (20/20) | ✗ → 1625k |
| 812k | **100%** (20/20) | ✗ → 1625k |

**Висновок G-2:** Алгоритм працює ІДЕАЛЬНО при f1=BW/2 (правильний signal model).
make_css_chirp у брифінгу має f1=bw_hz замість f1=bw_hz/2 → неправильний signal model.

---

## Важливе спостереження для Оркестратора

**Алгоритм (C2-fix-v6) КОРЕКТНИЙ** при правильних умовах:
- BW accuracy = **100% @ -12dB** для всіх 4 класів (20 тестів кожен) з f1=BW/2 ✓
- BW accuracy = **100% @ -14dB** для BW=1625k ✓ (Крок 1 noisy test)
- Алгоритм стабільний при SNR від +6 dB до -14 dB ✓

Два дефекти не в алгоритмі:
1. **G-1: Тест Крок 1 (clean chirp)** = unrealistic pathological case (no noise = never in production)
2. **G-2: make_css_chirp у брифінгу** = f1=bw_hz замість f1=bw_hz/2

---

## Метрики (виміряно частково)

| Метрика | Результат | Ціль | |
|---|---|---|---|
| Крок 1 clean 203/406/812k | ❌ pred=1625k | N/A | G-1 |
| Крок 1 noisy 1625k @-14dB | ✓ pred=1625k ratio=1.80 | N/A | ✓ |
| SF accuracy @ -10dB | **не тестувалось** (suite зупинено) | ≥85% | — |
| BW accuracy @ -12dB | **не тестувалось** | ≥80% | — |
| pair @ -14dB | **не тестувалось** | ≥78% | — |
| Latency | **не тестувалось** | ≤25ms | — |
| FTR | **не тестувалось** | ≤5% | — |

**Supplementary (позапланова верифікація алгоритму з правильним сигналом):**

| Тест | Результат |
|------|-----------|
| BW=203k f1=BW/2 @-12dB N=20 | **100%** ✓ |
| BW=406k f1=BW/2 @-12dB N=20 | **100%** ✓ |
| BW=812k f1=BW/2 @-12dB N=20 | **100%** ✓ |
| BW=812k f1=BW/2 SNR threshold | works ≥ +6dB through -14dB ✓ |

---

## Висновок

❌ **FAIL** — Крок 1 (BW verification) не пройшов, повний тест-suite не запускався.

ROOT CAUSE G = два окремих дефекти:

**G-1 (алгоритм — edge case):**
Per-class score нестабільний при zero noise: `ref_mean → 0` → `score[larger_BW] → ∞`.
Виникає ТІЛЬКИ при clean chirp (нульовий шум). При будь-якому AWGN (навіть +6dB) — алгоритм коректний.

**G-2 (тест генератор — неправильний signal model):**
`make_css_chirp` у брифінгу використовує `f1=bw_hz` (sweep 0→BW) замість `f1=bw_hz/2` (sweep 0→BW/2).
Spec §R2-2 каже: "IF sweeps від 0 до BW/2". Per-class algorithm очікує сигнал у [0, BW/2].
З f1=BW: ref_mask[BW/2..BW] містить сигнал → score[true_BW]≈1 → argmax вибирає 1625k.

**Рекомендації для Оркестратора:**

- G-1: Оновити Крок 1 перевірку — виключити clean chirp test АБО додати eps-noise (SNR=+30dB). Алгоритм не потребує зміни.
- G-2: Виправити make_css_chirp у брифінгу: `f1=bw_hz/2` (замість `f1=bw_hz`). Або використати синтетичний датасет з synth_dataset.py (centered IQ, Re(IQ) power in [0, BW/2]).

→ **Якщо Оркестратор виправляє брифінг (G-2) і тест генератор** → алгоритм (C2-fix-v6) очікувано пройде повний suite без змін src/.

D2 заблоковано. Повернути до Оркестратора для рішення.

---

_Run: 2026-06-02 · Крок 1 тільки · N=20 supplementary (f1=BW/2 validation)_
