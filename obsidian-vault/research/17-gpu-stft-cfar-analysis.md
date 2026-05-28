---
tags: [knowledge-builder, analysis, gpu, stft, cfar, cuda]
created: 2026-05-28
type: analysis
stage: 1
status: approved
score: 9.5/10
drive_id: 1ZnVM6lGf4imF33KY_D6UEdOUyf15eSZC4yu1HEr_KPk
source: 17_gpu_stft_cfar_analysis.md
---

# Аналіз GPU-акселерованого STFT + 2D OS-CFAR Pipeline

## Вердикт
9.5/10 — APPROVED з мінімальними уточненнями. Професійна специфікація рівня Senior CUDA Engineer.
**Рекомендація**: почати з **гібрида (CuPy + Custom CUDA Kernel)** для прототипу → міграція на чистий C++/CUDA для production.

## Сильні сторони
- Класичний GPU pipeline: pinned memory → STFT → CFAR → detection
- Гнучкі STFT (nfft 512-4096, overlap 50-87.5%)
- CUDA: shared memory, async streams, coalescing
- 2D OS-CFAR без CPU↔GPU copy
- Реалістичні KPI

## Критичні уточнення
1. **Memory bandwidth для STFT overlap 87.5%**: для nfft=4096 → 195k frames/s → 6.2 GB/s. RTX 3070 ~350 GB/s реальних. Рішення: 4-8 streams + batch windowing+FFT (8-16 frames). Стартувати з overlap=75%.
2. **OS-CFAR rank filter**: bitonic sort 512 → 4608 ops × 200M cells/s ≈ 920 GOPS. RTX 3070 ~8-12 TFLOPS реальних. Рішення: почати з CA-CFAR (O(1)), для OS — approximate rank через histogram або `thrust::nth_element` для малих вікон.
3. **Peak Detection + Connected Components**: 8-neighborhood має memory dependencies. Рішення: simple thresholding + NMS (non-maximum suppression) замість повного CC.

## Цільові параметри
- STFT: nfft 1024-4096, hop 1/4-1/8 nfft
- CFAR: train 16×8, guard 4×2, rank 0.75
- RTX 3070: ≥100 MS/s sustained, ≤10 ms p95 latency

## Залежності
- Імплементується у [[19-full-cuda-cpp-pipeline]]
- C++ скелет: [[08-stage1-oscfar-cpp]]
- Координується через [[06-tz5-hybrid-pipeline]]
- Latency tuning: [[11-latency-decision-fusion]]
