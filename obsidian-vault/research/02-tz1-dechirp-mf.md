---
tags: [knowledge-builder, tz, stage3, dechirping, matched-filter, lora-css]
created: 2026-05-28
type: tz
stage: 3
status: approved
version: "1.1"
drive_id: 1ap-IlA9ktxxskAv1T8IX44ETOnltv2DTAugnr00UcaQ
source: 02_tz1_dechirp_matched_filter.md
---

# ТЗ №1: Dechirping + Matched Filter Bank з blind estimation

## Статус
✅ APPROVED для реалізації (версія 1.1 — Final, 20 травня 2026).

## Призначення
Сліпе виявлення ELRS сигналів у реальному часі без попереднього знання SF / BW / hopping pattern.

## Наукове підґрунтя
- Vangelista (2017) — Dechirping + FFT оптимальний для LoRa CSS
- Knight et al. (2020) — Matched Filter Bank Pd ≥ 95% при SNR = -12 dB
- Elshabrawy & Robert (2019) — сліпа оцінка SF/BW через паралельну кореляцію
- ADRV9009: 200 MHz instantaneous bandwidth

## Виправлення проти v1.0
1. Додано **Circular Buffer + Overlapping Windows** (без них детектор працює тільки якщо сигнал з index 0)
2. **Точна формула LoRa chirp** з цілочисельним перенесенням (cumsum дає 5° фази помилки для SF12)
3. **Preamble Validator** — перевірка 8 однакових up-chirps (специфіка ELRS)
4. **CFO Correction перед dechirping** (CFO зміщує пік у FFT)
5. **CFAR-like adaptive threshold**

## Архітектура (GNU Radio Flowgraph)
```
RF Input (Aaronia/ADRV9009)
  → Complex Source (I/Q @ 1-2 MS/s)
  → Circular Buffer (Size: 2^SF_max × 4 overlap)
  → Python/CuPy Block (GPU-Accelerated):
     1. CFO Estimation & Correction (FFT-based)
     2. Parallel Dechirping (всі SF/BW combos)
     3. FFT + Peak Detection
     4. Preamble Validator (8 up-chirps + Sync Word)
     5. Parameter Estimation (SF/BW/CFO/STO/SNR)
  → Output Dict: {detected, sf, bw, cfo, snr}
```

## Очікувані метрики
- Pd ≥ 95% при SNR = -12 dB
- Латентність: вкладатися в 12-20 ms

## Залежності
- Виходить з [[01-system-architect]]
- Передує [[03-tz2-dwt-cwt]] (Stage 2 робить pre-screening для цього)
- Координується через [[06-tz5-hybrid-pipeline]]
- C++ реалізація скелета — [[08-stage1-oscfar-cpp]]
