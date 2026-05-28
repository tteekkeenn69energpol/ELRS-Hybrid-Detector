---
tags: [knowledge-builder, tz, architecture, pipeline, cascaded-detection, central]
created: 2026-05-28
type: tz
stage: all
status: approved
score: 9/10
drive_id: 1RVcTdm1QUuTNzKZN8TAZvG6wlRP0qhz7paVIcH7PBF4
source: 06_tz5_hybrid_multistage_pipeline.md
---

# ТЗ №5: Гібридний Multi-Stage Pipeline (центральна архітектура)

## Вердикт
9/10 — APPROVED. Професійна архітектура промислового рівня. **Каскадний підхід — єдиний спосіб поєднати швидкість, точність та стійкість до завад.**

## Каскад
```
RF (ADRV9009 200 MHz / Aaronia)
  → Stage 1: 2D OS-CFAR (C++/CUDA, 100 MS/s, фільтрує до 1-5% потоку)
  → Stage 2: Blind Estimator DWT+CWT (Python/CuPy, тільки кандидати)
  → Stage 3: Dechirp+MF (Python/CuPy, верифікація SF/BW)
  → Stage 4: NN Verifier (ONNX, тільки "підозрілі")
  → Decision Fusion (weighted voting + hysteresis)
```

## Сильні сторони
- Cascaded detection: швидкі етапи фільтрують, складні уточнюють
- Unified Configuration (YAML)
- GPU-first: CUDA streams + pinned memory
- Decision Fusion: weighted voting + hysteresis → знижує FAR
- Поетапні метрики приймання

## Критичні проблеми
1. **100 MS/s в Python**: 800 MB/s I/Q потік. Python GIL + CUDA memcpy bottleneck. Рішення: lock-free queues + async streams + pre-allocated GPU buffers.
2. **ADRV9009 інтеграція**: JESD204B (12+ lanes @ 3.125 Gbps). Розподіл: Stage 1-2 FPGA, Stage 3-5 PC. Або весь pipeline PC + ADRV9009 як ADC.
3. **NN навчання**: ~9.6M синтетичних + 10k реальних, 2-4 дні pre-training на RTX 3070.
4. **Реалістичність таймінгів**: вимагає корекції під CPU/GPU/FPGA зони.

## Цільові метрики
- Pd ≥ 95% при SNR -12 dB
- Загальна латентність ≤ 50 ms
- FAR ≤ 1%
- Throughput 100 MS/s sustained

## Залежності
- Імпл'е Stage 1: [[08-stage1-oscfar-cpp]], [[19-full-cuda-cpp-pipeline]]
- Імпл'е Stage 2: [[09-stage2-blind-estimator-py]]
- Імпл'е Stage 4: [[13-stage4-nelora-verifier-onnx]]
- Інтеграція з GR: [[07-oot-gnuradio-skeleton]], [[10-gnuradio-flowgraph]]
- Latency + Fusion: [[11-latency-decision-fusion]]
- Hardware: [[12-adrv9009-artix7-migration]]
