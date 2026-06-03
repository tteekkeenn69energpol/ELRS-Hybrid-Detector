---
tags: [stage-2, knowledge-builder, tz, pipeline, multi-stage, architecture]
created: 2026-05-29
type: specification
stage: 1
status: done
source: TZ_05_Hybrid_MultiStage_Pipeline.md
drive_id: 1QcJP2tUabiaVXArkQd8tpUCZV0X4Pl1H
---

# ТЕХНІЧНЕ ЗАВДАННЯ №5
**Розробка повного гібридного реал-тайм детектора ExpressLRS (Multi-Stage Pipeline)**

**Замовник:** Tekken Corp. Defense Tech Division
**Дата:** 20 травня 2026
**Мета:** Промисловий рівень гібридна система детекції ELRS/MiELRS/ZeLRS з максимальною Pd в умовах реального ефіру.

---

## 1. Загальна Архітектура (Multi-Stage Pipeline)

```
Stage 0 – Signal Acquisition
SoapySDR (Aaronia) / ADRV9009 → CUDA Pinned Memory

Stage 1 – Fast Wideband Trigger (2D OS-CFAR)    ← CLOSED ✅
Stage 2 – Blind Parameter Estimation (DWT + CWT/SST)
Stage 3 – Fine Detection (Dechirping + Matched Filter Bank)
Stage 4 – Deep Neural Verification (NELoRa-style CNN/Transformer)
Stage 5 – Decision Fusion & Tracking
```

---

## 2. Детальний розпис етапів розробки

### Етап 1 (ЗАВЕРШЕНО ✅)
- Stage 1: 2D OS-CFAR — Pfa=0/10.5M, Throughput=86.27 MS/s.
- Коміти: 308f60d (C), e3668ec (T), 62c54cc (D), 1056283 (KB-extra).

### Етап 2: Blind Parameter Estimation (3–4 тижні) ← ПОТОЧНИЙ
- Stage 2 (DWT + CWT/SST).
- Метрики: SF ≥ 85% @ -10 dB, BW ≥ 80% @ -12 dB, pair ≥ 78% @ -14 dB.
- Latency ≤ 25 мс.

### Етап 3: Fine Detection (4 тижні)
- Stage 3: Dechirping + Matched Filter Bank.
- Pd ≥ 93% при SNR = -14 dB.
- CFO/STO корекція в реальному часі.

### Етап 4: Neural Verification (5–6 тижнів)
- Stage 4: NELoRa-style CNN.
- ONNX + TorchScript, inference ≤ 8 мс.
- Pd ≥ 90% при SNR = -17 dB.

### Етап 5: Інтеграція та Fusion (4 тижні)
- Decision Fusion Engine (weighted voting + hysteresis).
- End-to-end pipeline з CUDA Streams.
- GNU Radio OOT блок `gr-elrs_detector`.

---

## 3. Загальні вимоги

- **Мова:** Python 3.10+, CUDA 12.x, PyTorch 2.4+
- **Профілювання:** кожен kernel + етап — вбудований таймер.
- **Конфігурація:** всі параметри виносяться в `UnifiedConfiguration` (JSON/YAML).
- **Тестування:** Unit + Integration + System + стендові тести.

---

## 4. Приймальні випробування (Final Acceptance Criteria)

1. Стабільна робота на **100 MS/s** без dropped samples ≥ 30 хвилин.
2. Pd ≥ 95% при SNR = -12 dB на реальних сигналах.
3. Pd ≥ 80% при SNR = -16 dB з завадами.
4. Pfa ≤ 0.1%.
5. Повна документація + приклади запуску.

---

## Посилання

- [[06-tz5-hybrid-pipeline]] — аналіз TZ#5 (KB-2)
- [[docs/pipeline-overview]] — архітектурний огляд
- [[stage2-tz-dwt-cwt]] — Stage 2 spec
- [[stage2-tz-dechirp-mf]] — Stage 3 spec
- [[stage2-tz-gnuradio]] — GNU Radio інтеграція
- [[logs/decisions-log]] — рішення Stage 1 (закрито)
