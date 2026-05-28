---
tags: [external, KB-extra, group-8, fmcw, radar, reconfigurable, fpga, ieee]
created: 2026-05-28
type: paper
stage: 1
source_url: https://www.researchgate.net/publication/389083744_Design_of_Reconfigurable_Radar_Signal_Processor_for_Frequency_Modulated_Continuous_Wave_Radar
status: partial
ieee_doc: 10891638
venue: IEEE
---

# Design of Reconfigurable Radar Signal Processor for FMCW (R-RSP)

## Цитування
*Design of Reconfigurable Radar Signal Processor for Frequency-Modulated Continuous Wave Radar.* IEEE (Xplore document 10891638).
Автори не екстраговано (ResearchGate 403 + IEEE не відкриває без auth).

## Короткий зміст (з WebSearch)
Запропоновано **R-RSP** (Reconfigurable Radar Signal Processor) для FMCW. Архітектура містить **FFT та CFAR IP modules** як reconfigurable blocks.

## Архітектура (типова для FMCW)
- ADC → FIR filter → FFT (range) → 2nd FFT (Doppler) → CFAR → peak detection
- **R-RSP** — параметризується runtime: bandwidth, range resolution, chirp duration

## Релевантність до проєкту
- **FPGA Stage 1 паттерн** — FFT IP + CFAR IP як reconfigurable blocks — точно те що треба для [[12-adrv9009-artix7-migration]]
- FMCW != LoRa CSS, але **обчислювальна структура схожа** (FFT + threshold detection)
- Концепт "reconfigurable" (зміна параметрів runtime) — наш UnifiedConfiguration ([[06-tz5-hybrid-pipeline]])
- IEEE 10891638 — варто витягнути авторів коли буде доступ

## Related papers (з search)
- *Improvement of Radar Capabilities by Reconfigurable DSP* — Academia.edu
- *Low-Cost FMCW Radar with Configurable Signal Processor* — ResearchGate 333827691
- *FPGA Implementation of Efficient FFT Processor for FMCW* — PMC8512539
- *High-Resolution FMCW for Drone Detection* — Vu Hop 2024 (IET Radar)

## Посилання
- [[12-adrv9009-artix7-migration]] — FPGA Stage 1
- [[06-tz5-hybrid-pipeline]] — reconfigurable pipeline
- [[ext-fmcw-40]] — Venter thesis (duplicate of [[25-venter-sdr-pulse-doppler-gpu]])
- [[ext-cuda-gpu-25]] — NVIDIA PVA RadarCFAR (HW alternative)
