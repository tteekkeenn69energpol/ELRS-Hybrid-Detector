---
tags: [knowledge-builder, code, gnuradio, flowgraph, grc, soapysdr]
created: 2026-05-28
type: code
stage: all
status: ready
drive_id: 190G2SDpFThmVm1iVdn4eejLND5ZNims29GkkboDXO1Q
source: 10_gnuradio_flowgraph.md
---

# elrs_full_pipeline.grc + інтеграція SoapySDR (Aaronia)

## Призначення
Готовий .grc файл (`examples/elrs_full_pipeline.grc`), що з'єднує всі етапи pipeline.

## Структура flowgraph
```
SoapySDR Source (Aaronia)
  → Throttle (debug only)
  → Stream-to-Vector (fft_size)
  → C++ OS-CFAR Block
       ↓ (message port: triggers)
  → Python Blind Estimator (Stage 2)
       ↓
  → Python Dechirp Detector (Stage 3)
       ↓
  → Python Neural Verifier (Stage 4)
       ↓
  → Decision Fusion → File Sink / Logger
```

## Variables (за замовчуванням)
- `samp_rate = 2e6` (можна підняти до 30.72e6/100e6)
- `center_freq = 868e6` (або 915e6 для ELRS US)
- `gain = 30`
- `cfar_threshold_db = 4.0`
- `cfar_rank = 0.75`
- `max_sf = 12`

## Зауваження
- Vector sizes критично важливі для 100 MS/s (див. [[11-latency-decision-fusion]])
- Без C++ Stage 1 → OVERRUN
- Аналог для standalone CFAR — `NEW_CODE/CFAR_2D_ELRS_915_30MSPS_2048.grc`

## Залежності
- Координує всі Stage 1-4
- Запускає [[08-stage1-oscfar-cpp]], [[09-stage2-blind-estimator-py]], [[13-stage4-nelora-verifier-onnx]]
- Tuning: [[11-latency-decision-fusion]]
