---
tags: [knowledge-builder, code, gnuradio, oot-module, integration]
created: 2026-05-28
type: code
stage: all
status: approved
score: 10/10
drive_id: 15IMY-c7cii9zdOAIUduyaUOFy9Mt9i2SRONT4Nb4jNM
source: 07_oot_gnuradio_skeleton.md
---

# Скелет OOT GNU Radio модуля

## Вердикт
10/10 — APPROVED. **Ідеальна архітектура** інтеграції з GNU Radio.

## Ключові принципи
- **gr_modtool** для генерації структури OOT-модуля
- **C++ для Stage 1** (OS-CFAR) — Python GIL + 100 MS/s = dropped samples; С++ обов'язково
- **Python/CuPy для Stage 2-4** (швидка зміна алгоритмів, GPU без CUDA kernels)
- **Message Passing (PMT)** — Stage 2-4 не блокують потік Stage 1
- **SoapySDR** для Aaronia + ADRV9009
- **Dynamic Parameters** — зміна threshold на льоту

## Архітектура шарів
```
Layer 1: C++ Core (high performance)
  os_cfar_2d_impl.cc:
    100 MS/s → FFT + CFAR → peaks
    Output: pmt::cons("trigger", "coords") + gr::tag_t
    Гарантує 0 dropped samples

Layer 2: Python/CuPy Glue (flexibility)
  Blind_Estimator + Dechirp_Detector (Sync Blocks):
    Subscribe Message Port
    On trigger: read ~50 ms навколо піку
    DWT/CWT/Dechirp на GPU
```

## Команди старту
```bash
gr_modtool new -t general elrs_detector
cd gr-elrs_detector
gr_modtool add -t general -l cpp os_cfar_2d
```

## Не робити
- Не передавати весь потік `out_sig` далі по конвеєру — тільки tags/messages з координатами піку
- Не реалізовувати Stage 1 на Python

## Залежності
- Stage 1 деталі: [[08-stage1-oscfar-cpp]]
- Stage 2 код: [[09-stage2-blind-estimator-py]]
- Готовий flowgraph: [[10-gnuradio-flowgraph]]
- Координація через [[06-tz5-hybrid-pipeline]]
