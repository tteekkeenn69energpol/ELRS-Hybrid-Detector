---
tags: [stage-2, knowledge-builder, confidence-gate, fusion, synthesis]
created: 2026-05-29
type: synthesis
stage: 2
status: done
---

# Confidence Gate — Synthesis Note

Конспект combined score, порогів 0.4/0.7, та false-trigger control для Stage 2 Confidence Gate.

---

## Призначення

Confidence Gate є **фінальним фільтром Stage 2**, що:
1. Відкидає низькоякісні оцінки (noise triggers від Stage 1)
2. Визначає routing: пряме в Stage 3 або через Stage 4 (Neural)

---

## Combined Score Formula

```
confidence = w_dwt × DWT_score + w_cwt × CWT_energy_ratio

де:
  DWT_score     = peak_autocorr[symbol_len] / autocorr.mean()
                  (нормована "гостроть" піку, ≥ 1.0)
  CWT_energy_ratio = energy[best_bw] / energy.mean()
                     (ratio best BW до середнього, ≥ 1.0)
  w_dwt = w_cwt = 0.5   (рівні ваги, якщо не відкалібровано)
```

### Нормалізація до [0, 1]

Обидва компоненти можуть бути >> 1 при сильних сигналах.
Нормалізуємо через sigmoid або min-max:

```python
def normalize_score(raw_score, low_threshold=1.0, high_threshold=10.0):
    return min(1.0, max(0.0, (raw_score - low_threshold) / (high_threshold - low_threshold)))

confidence = 0.5 * normalize_score(dwt_score) + 0.5 * normalize_score(cwt_energy_ratio)
```

---

## Порогова логіка

```python
if confidence < 0.4:
    # REJECT: скидаємо тригер, Stage 2 output = None
    return None

elif confidence >= 0.7:
    # DIRECT to Stage 3: висока впевненість, пропускаємо Neural
    return PDU(sf=sf, bw=bw, confidence=confidence, route='stage3_direct')

else:  # 0.4 <= confidence < 0.7
    # NEURAL: відправляємо в Stage 4 для верифікації
    return PDU(sf=sf, bw=bw, confidence=confidence, route='stage4_neural')
```

### Інтерпретація порогів

| Поріг | Значення |
|-------|---------|
| < 0.4 | Скоріш за все шум або дуже слабкий сигнал — відкидати |
| 0.4–0.7 | Можливий сигнал, але невпевнено — Neural верифікація |
| ≥ 0.7 | Впевнена оцінка — Stage 3 напряму |

---

## False-Trigger Control

### Джерела false triggers
1. Stage 1 OS-CFAR хибно спрацьовує на noise burst → Stage 2 отримує noise buffer
2. CWT energy ≠ chirp (наприклад, тональний сигнал, WiFi preamble)
3. DWT периодичність у non-ELRS сигналі

### Механізми контролю

**1. Holdoff timer (100 мс):**
```python
if time.time() - self.last_trigger_time < 0.1:
    return None  # Ignore within holdoff window
self.last_trigger_time = time.time()
```

**2. SF consistency check:**
```python
# SF оцінки у sliding window мають бути консистентними
if len(self.sf_history) >= 3:
    if np.std(self.sf_history[-3:]) > 1.5:  # too noisy
        confidence *= 0.5  # penalty
```

**3. Chirp rate verification:**
```python
# Перевіряємо що estimated BW та SF дають реалістичний chirp rate
expected_chirp_rate = bw / (2**sf)
if abs(measured_chirp_rate - expected_chirp_rate) / expected_chirp_rate > 0.15:
    confidence *= 0.3  # heavy penalty
```

**4. Минімальна тривалість сигналу:**
```python
# Якщо signal duration < 0.5 × preamble_duration → reject
min_duration = 8 * (2**sf / bw)  # 8 up-chirps
if buffer_duration < min_duration * 0.5:
    return None
```

---

## Калібрування порогів

### На синтетичних даних (T2-1)

```python
# Для кожного SNR рівня та SF/BW пари:
# 1. Обчислити confidence розподіл для SIGNAL
# 2. Обчислити confidence розподіл для NOISE
# 3. Знайти оптимальні пороги (ROC curve)

# Target: false trigger rate ≤ 5% (T2-6)
# При цій умові визначити поріг 0.4

# Target: SF+BW accuracy ≥ 78% @ -14 dB (T2-4)
# При цій умові визначити поріг 0.7
```

### Очікувана поведінка при різних SNR

| SNR (dB) | DWT score | CWT ratio | confidence | Route |
|----------|-----------|-----------|------------|-------|
| +10 | 8.5 | 7.2 | ~0.85 | stage3_direct |
| 0 | 4.1 | 3.8 | ~0.65 | stage4_neural |
| -10 | 2.3 | 2.1 | ~0.40 | stage4_neural / reject |
| -14 | 1.5 | 1.3 | ~0.25 | reject |

*Значення приблизні — точні порогові таблиці після T2-1 калібрування*

---

## Зв'язок з Stage 4 (Neural) та Stage 5 (Fusion)

```
Stage 2 Confidence Gate
    |
    ├── conf < 0.4 → DISCARD
    |
    ├── conf ≥ 0.7 → Stage 3 (direct)
    |                    ↓
    |               Stage 5 (Fusion) weight = 0.8
    |
    └── 0.4 ≤ conf < 0.7 → Stage 4 Neural
                               ↓
                          Stage 5 (Fusion) weight = 0.6
```

Stage 5 Decision Fusion використовує `confidence` як **weight** для weighted voting.

---

## False Trigger Rate (T2-6 target: ≤ 5%)

False trigger = Stage 2 output ≠ None для noise input.

```python
# Test: 10,000 pure noise buffers through Stage 2
# Count outputs where confidence ≥ 0.4
false_trigger_rate = n_outputs / 10000

# Target: ≤ 5% → поріг 0.4 повинен відкидати ≥ 95% noise
```

---

## Посилання

- [[stage2-arch-principles]] — NotebookLM: Q37 Fallback, Q18 Adaptive thresholds
- [[stage2-dwt-cwt-questions]] — Q5, Q18, Q32, Q37, Q45
- [[stage2-tz-dwt-cwt]] — ТЗ Stage 2 (verification section)
- [[03-tz2-dwt-cwt]] — confidence gate 0.4/0.7 (KB-2)
- [[stage2-key-dwt]] — DWT_score source
- [[stage2-key-cwt]] — CWT_energy_ratio source
- [[11-latency-decision-fusion]] — Stage 5 Decision Fusion weights
