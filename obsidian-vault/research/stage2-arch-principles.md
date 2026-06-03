---
tags: [stage-2, knowledge-builder, dwt, cwt, architecture, notebooklm, sst]
created: 2026-05-29
type: analysis
stage: 2
status: done
drive_folder_id: 1AjaKtXUvsCoKfdeBpYp8gUn3iTs5JpCc
drive_doc_id: 1NExLnRvTtnkV6euXQTdXwPtZiJGtJAIbkcCHFRNH0wo
source: "🔹 Section 1: Architecture & Principles.docx (Google Drive)"
---

# Section 1: Architecture & Principles — DWT/CWT для LoRa/ELRS

Відповіді NotebookLM на базові питання архітектури Stage 2.

---

## 1. DWT MRA та LoRa SF

DWT (Discrete Wavelet Transform) з Multi-Resolution Analysis (MRA) є **multi-scale matched filter** для LoRa пreambles. Працює через виявлення **energy surges** при frequency wraps на boundaries символів.

### Ключові факти:
- SF визначає slope та symbol duration: **Ts = 2^SF / BW**
- DWT detail coefficients рівня 3–4 показують **periodic parabolic pattern** з інтервалом = Ts
- FFT над DWT coefficients дає пік на частоті, унікальній для кожного SF

### Приклад (Level 3, 4× oversampling):
- SF10: пік DWT-FFT при 8 Hz
- SF11: пік при 4 Hz (подвійна symbol duration)

### Точність DWT-FFT pipeline:
- **99.5% accuracy при SNR ≥ -10 dB**
- Успішна локалізація до -20 dB для SF9–10
- Складність: **O(N + N log N)** vs O(M·N²) для parallel correlators

---

## 2. Оптимальні рівні декомпозиції

| Oversampling | Оптимальний рівень | Примітка |
|-------------|-------------------|----------|
| 4× | Level 3 | |
| 8× | Level 4 | |

**Оптимальний розмір вікна:** 8 символів SF10
- Достатньо для SF12 (≥ 2 повних символи)
- Для SF7: сигнал займає ≥ 1/8 вікна

---

## 3. CWT vs STFT та SST

**STFT обмежений:** Heisenberg-Gabor uncertainty — жорсткий trade-off між time/freq resolution.

**CWT покращує:** multi-resolution, але energy ще "розмита" по adjacent scales.

**SST (Synchrosqueezing):** reassignment operator, переміщує коефіцієнти вздовж frequency axis до true IF ridge.
- **First-order SST:** може мати estimation bias для LFM сигналів (ELRS)
- **Second-order SST (SSST):** включає chirp rate у phase correction → near-perfect energy concentration
- Точність при SNR до -10 dB

---

## 4. Hybrid DWT → CWT каскад (наша архітектура)

```
DWT stage (O(N), coarse):
  → SF identification через periodicity detection
  → Coarse BW tracking через dyadic sub-bands
  → Packet локалізація (навіть при SNR -20 dB)
  
  ↓ candidate + time window
  
CWT/SST stage (fine):
  → High-resolution ridge extraction
  → Fine BW та chirp slope estimation
  → Overcoming Gabor limit
  
  → {SF, BW, confidence, t_offset}
```

**Ключова перевага:** CWT запускається тільки на локалізованому сегменті → зменшення обчислень.

---

## 5. Вибір материнського вейвлету

| Вейвлет | Переваги | Недоліки |
|---------|----------|----------|
| **Biorthogonal** | Найвища accuracy при SNR < -5 dB | Складніший для реалізації |
| Symlet 12 | Краще за Daubechies при SNR < -5 dB | Загалом гірше за Biorthogonal |
| Morlet | Відмінна multi-scale локалізація chirps | Чутливіший до шуму ніж STFT |
| Daubechies 8 | Denoising (ізоляція HF шуму) | Поступається Biorthogonal |

**Рекомендація для Stage 2:** sym5 (TZ#2) або biorthogonal для екстремально низького SNR.

---

## 6. STO Invariance

Стандартний DWT **не** має translation invariance (через decimation).

**Рішення:**
1. **SWT (Stationary Wavelet Transform)** — undecimated, translation invariant
2. **MODWT (Maximal Overlap DWT)** — undecimated, зберігає temporal alignment
3. **DT-CWT (Dual-Tree Complex WT)** — approximate shift invariance
4. **Wavelet Scattering (ScatNet)** — CFO invariant feature vectors

**Практичне рішення для Stage 2:** Dynamic window alignment — DWT як edge detector визначає hop boundaries, потім CWT вікно центрується по ним.

---

## 7. Sliding Window Overlap

| Overlap | Поведінка |
|---------|-----------|
| ≥ 90% | Стабільні estimates, менше timing errors |
| 66.6% (~1/3 advancement) | Оптимум для multi-rate ELRS |
| < 50% | Timing errors 8–15 мс (> ELRS packet interval) |

**Наша конфігурація:** 75% overlap (відповідно до [[17-gpu-stft-cfar-analysis]] та архітектурного рішення).

---

## 8. DWT Energy vs Noise

**DWT discriminates noise від ELRS через:**
- Wideband noise: energy розподілена **випадково** по всіх рівнях і часових зсувах
- ELRS сигнал: energy surges **строго периодичні** з інтервалом Tsym

**Обмеження:** чисто energy-based metrics без temporal analysis недостатні. Потрібен DWT-FFT pipeline, що витягує **частоту** energy surges, а не просто їх magnitude.

---

## 9. Порівняння DWT vs Matched Filter

| Параметр | Matched Filter | DWT-FFT |
|----------|---------------|---------|
| Складність | O(M·N²) | O(N + N log N) |
| Априорні знання | Потрібні SF/BW шаблони | Сліпий |
| Обладнання | Паралельні RF chains | Single SDR frontend |
| SNR floor | Теоретично оптимальний | -10 dB (99.5%), -20 dB з обмеженнями |

---

## 10. Обмеження DWT (для DSP Research)

1. **SNR detection floor ~-10 dB** для reliable detection
2. **"Chicken-and-egg" window limit:** 8-SF10 symbol window — оптимум
3. **Harmonic interference:** DWT filter transition-bands → false SF peaks
4. **Dyadic resolution:** BW estimation обмежена power-of-two sub-bands

---

## Критичні висновки для R2-1..R2-3

- **R2-1 (DWT SF spec):** Level 3–4 залежно від oversampling; autocorrelation Detail coefficients; вікно = 8 × SF10 symbols
- **R2-2 (CWT BW spec):** SST (second-order) для ELRS; Morlet або biorthogonal при низькому SNR
- **R2-3 (Confidence gate):** combined DWT periodicity score + CWT energy; пороги 0.4/0.7 обґрунтовані

---

## Посилання

- [[stage2-dwt-cwt-questions]] — 45 питань для аналізу
- [[stage2-key-dwt]] — synthesis DWT
- [[stage2-key-cwt]] — synthesis CWT/SST
- [[stage2-tz-dwt-cwt]] — ТЗ Stage 2
- [[03-tz2-dwt-cwt]] — попередній аналіз (KB-2)
- [[09-stage2-blind-estimator-py]] — Python референс реалізації
