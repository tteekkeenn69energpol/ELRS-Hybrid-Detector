---
tags: [knowledge-builder, tz, analysis, stage2, dwt, cwt, blind-estimator]
created: 2026-05-28
type: analysis
stage: 2
status: approved-with-modifications
score: 7.5/10
drive_id: 1Vbs1zRNZwq4G2huO4NoKEcJRsWSfzNrZgs9567Uw998
source: 03_tz2_dwt_cwt_blind_estimator.md
---

# ТЗ №2: DWT + CWT Blind Parameter Estimator

## Вердикт
7.5/10 — APPROVED з модифікаціями. Концепція науково обґрунтована, але є критичні обмеження. **Використовувати як pre-screening етап перед Dechirping+MF** з ТЗ №1.

## Сильні сторони
- DWT для SF: періодичність вейвлет-коефіцієнтів корелює з тривалістю символу
- CWT + Synchrosqueezing: краща часо-частотна локалізація для чирпів
- Blind estimation: критично для невідомого джерела

## Критичні проблеми
1. **DWT для CSS**: LoRa — частотна модуляція, не амплітудна. |IQ| втрачає фазу → періодичність розмивається. При SNR < -10 dB автокореляція стає шумовою. **Ризик**: точність SF < 70% при -12 dB.
2. **Складність CWT+SST**: O(N × n_scales × log N). Для 50 ms @ 2 MS/s ~10-50 ms CPU + SST overhead ×2-3. **Не вкладається у 12 ms.**
3. **Немає GPU**: pywt і ssqueezepy лише на CPU. Перенос даних CPU↔GPU вбиває швидкість.
4. **Чутливість до CFO**: потрібна груба корекція ДО хвильового аналізу.

## Рекомендована архітектура v1.1
```
I/Q (50-100 ms)
 → Coarse CFO Est. (FFT-based)
 → DWT Pre-Screen (швидкий, low-res, candidate top-2 SFs)
 → CWT Refinement (Morlet, focused scales, тільки для кандидатів)
 → Confidence Gate:
    if conf > 0.8 → Dechirping (ТЗ#1)
    if conf < 0.5 → fallback to brute-force
 → Output: {sf, bw, confidence}
```

## Залежності
- Pre-screening для [[02-tz1-dechirp-mf]]
- Імплементація — [[09-stage2-blind-estimator-py]]
- Координується через [[06-tz5-hybrid-pipeline]]
