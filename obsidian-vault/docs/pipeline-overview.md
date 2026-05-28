---
tags: [knowledge-builder, architecture, pipeline, overview]
created: 2026-05-28
status: done
type: overview
---

# ELRS Hybrid Detector — Каскадна архітектура (Stage 1→2→3→4)

Огляд побудований з 19 документів KB-2 (див. [[../research/sources]]).
Центральний документ: [[../research/06-tz5-hybrid-pipeline]] (9/10 APPROVED).

## Загальна схема каскаду

```
                ┌──────────────────────────────────────────┐
                │   RF Frontend                            │
                │   - Lab: Aaronia SPECTRAN V6 + SoapySDR  │
                │   - Field: ADRV9009 + Artix-7 + JESD204B │
                │   - 200 MHz instantaneous BW             │
                └────────────────────┬─────────────────────┘
                                     │ 100+ MS/s I/Q
                                     ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ STAGE 1: 2D OS-CFAR Trigger      (C++/CUDA — 0% Python)     │
   │ • STFT (nfft 1024-4096, overlap 50-75%)                     │
   │ • Magnitude² + log10                                        │
   │ • 2D OS-CFAR (train 16x8, guard 4x2, rank 0.75)             │
   │ • NMS peak detection                                        │
   │ • Output: PMT trigger {time, freq, power}                   │
   │ • Filters ~95-99% of stream                                 │
   │ Latency goal: ≤10 ms p95, 0 dropped samples                 │
   │ See: [[../research/08-stage1-oscfar-cpp]],                  │
   │      [[../research/17-gpu-stft-cfar-analysis]],             │
   │      [[../research/19-full-cuda-cpp-pipeline]]              │
   └────────────────────┬────────────────────────────────────────┘
                        │ PMT messages
                        │ (~1-5% of stream)
                        ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ STAGE 2: Blind Parameter Estimator (Python/CuPy)            │
   │ • Coarse CFO correction (FFT-based)                         │
   │ • DWT pre-screen → candidate SFs (top-2)                    │
   │ • CWT refinement (Morlet) → BW                              │
   │ • Confidence gate                                           │
   │ Latency goal: ≤25 ms                                        │
   │ See: [[../research/03-tz2-dwt-cwt]],                        │
   │      [[../research/09-stage2-blind-estimator-py]]           │
   └────────────────────┬────────────────────────────────────────┘
                        │ {sf, bw, confidence}
                        ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ STAGE 3: Dechirp + Matched Filter Bank (Python/CuPy)        │
   │ • Circular buffer + overlapping windows                     │
   │ • Parallel dechirping (all candidate SF/BW)                 │
   │ • FFT + peak detection                                      │
   │ • Preamble validator (8 up-chirps + Sync)                   │
   │ • CFO/STO/SNR refinement                                    │
   │ Latency goal: ≤20 ms                                        │
   │ Optional offline verifier: Wigner-Hough Transform           │
   │ See: [[../research/02-tz1-dechirp-mf]],                     │
   │      [[../research/04-tz3-wigner-hough]] (offline)          │
   └────────────────────┬────────────────────────────────────────┘
                        │ Verified detection + params
                        ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ STAGE 4: Neural Verifier (ONNX Runtime, async)              │
   │ • EfficientNet-B3 / ViT-Small on spectrogram                │
   │ • Multi-task: detect + params + confidence + embeddings     │
   │ • Triggered ONLY for confidence ∈ [0.4, 0.7] (gating)       │
   │ • RF Fingerprinting via embeddings (Stage 4.5)              │
   │ Latency goal: ≤8 ms (GPU) / ≤15 ms (Edge INT8)              │
   │ See: [[../research/05-tz4-nelora]],                         │
   │      [[../research/13-stage4-nelora-verifier-onnx]],        │
   │      [[../research/15-rf-fingerprinting-tz]]                │
   └────────────────────┬────────────────────────────────────────┘
                        │ {detected, sf, bw, device_id, conf}
                        ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ DECISION FUSION (weighted voting + hysteresis)              │
   │ • Weights: CFAR 0.2, Dechirp 0.4, NN 0.3, Estim 0.1         │
   │ • Hysteresis prevents flicker at threshold                  │
   │ • NN can be overruled by classical stages (new jammer types)│
   │ See: [[../research/11-latency-decision-fusion]]             │
   └────────────────────┬────────────────────────────────────────┘
                        ▼
                ┌──────────────────────┐
                │ Logger / Hop-Map     │
                │ Whitelist/Blacklist  │
                │ FHSS Tracker → Jammer│
                └──────────────────────┘
```

## Цільові метрики (end-to-end)

| Метрика | Значення | Джерело |
|---------|----------|---------|
| Pd | ≥ 95% @ SNR -12 dB | [[../research/06-tz5-hybrid-pipeline]] |
| Pfa / FAR | ≤ 1% | [[../research/06-tz5-hybrid-pipeline]] |
| Throughput | 100 MS/s sustained | [[../research/06-tz5-hybrid-pipeline]] |
| End-to-end latency | ≤ 50 ms | [[../research/06-tz5-hybrid-pipeline]] |
| Stage 1 dropped samples | 0 | [[../research/08-stage1-oscfar-cpp]] |

## Розподіл CPU / GPU / FPGA

| Стадія | Lab (PC only) | Field (FPGA+PC) | Edge (Jetson/Coral) |
|--------|---------------|------------------|---------------------|
| Stage 1 (CFAR) | C++/CUDA on PC | Artix-7 HDL | TensorRT FP16 |
| Stage 2 (Blind) | Python/CuPy | Python/CuPy | Python/TFLite |
| Stage 3 (Dechirp) | Python/CuPy | Python/CuPy | Python/TFLite |
| Stage 4 (NN) | ONNX+CUDA | ONNX+CUDA | TensorRT INT8 / Coral Edge TPU |

## Ключові архітектурні принципи

1. **Cascade**: швидкі стадії фільтрують потік, складні уточнюють → економія компуту
2. **Message-based**: Stage 2-4 не блокують Stage 1 (PMT через GNU Radio)
3. **Hot-reload**: всі пороги (CFAR threshold, NN confidence) у YAML/dynamic vars
4. **Observability**: Prometheus metrics + systemd watchdog ([[../research/16-edge-ai-fhss-tracker]])
5. **Open architecture**: feature extractors / decision plugins (для RF fingerprint, FHSS predictor)

## Найбільші ризики (зведено з аналізів)

| Ризик | Стадія | Джерело | Мітигація |
|-------|--------|---------|-----------|
| Python GIL + 100 MS/s | 1 | [[../research/07-oot-gnuradio-skeleton]] | Stage 1 виключно на C++ |
| DWT не працює на CSS | 2 | [[../research/03-tz2-dwt-cwt]] | DWT тільки pre-screen, fallback brute-force |
| WVD cross-terms + O(N²) | 3-offline | [[../research/04-tz3-wigner-hough]] | Pseudo-WVD + focused Hough |
| Synthetic→Real gap для NN | 4 | [[../research/05-tz4-nelora]] | Domain Adaptation + RF-aware augmentation |
| Memory bandwidth для STFT 87.5% overlap | 1 | [[../research/17-gpu-stft-cfar-analysis]] | overlap 75%, batch frames, 4-8 streams |
| Artix-7 без ARM | 1-hw | [[../research/12-adrv9009-artix7-migration]] | MicroBlaze + adrv9009_api |
| FHSS невпійманий хоп | jammer | [[../research/16-edge-ai-fhss-tracker]] | FHSS Tracker (LFSR reverse + cyclostationary) |

## Roadmap (Stage 1 пріоритет — поточний)

Активний фокус: **Stage 1 — 2D OS-CFAR standalone** (див. CLAUDE.md проекту, PROGRESS.md).
Подальші стадії розробляються після підтвердження Stage 1 throughput ≥ 80 MS/s та Pfa ≤ 1%.

## Дослідницький beck-log

45 відкритих питань — див. [[../research/18-research-questions]].
Конкурентний контекст — [[../research/14-commercial-defence-analysis]].
