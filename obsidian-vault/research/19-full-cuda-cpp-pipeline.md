---
tags: [knowledge-builder, code, cuda, cpp, stft, oscfar, production, peak-detect]
created: 2026-05-28
type: code
stage: 1
status: ready
drive_id: 1u1MBG4g9JpRFzl-meG0LM57DqYwc2klbJ8jd6J2Cqrc
source: 19_full_cuda_cpp_pipeline.md
---

# Повний CUDA C++ Pipeline: STFT + 2D OS-CFAR + Peak Detector

## Призначення
Максимально детальна продакшн-готова реалізація Stage 1 для 100+ MS/s real-time. Senior CUDA Engineer-level.

## Структура проєкту
```
gpu_stft_cfar_pipeline/
├── CMakeLists.txt
├── include/
│   ├── gpu_stft_cfar.hpp          # Public API
│   ├── cuda_kernels.cuh           # Kernel declarations
│   └── utils.cuh                  # CUDA_CHECK, timing
├── src/
│   ├── gpu_stft_cfar.cu           # Main class
│   ├── kernels/
│   │   ├── stft_kernel.cu         # Optimized STFT
│   │   ├── magnitude_db_kernel.cu # |X|² + log10
│   │   ├── os_cfar_2d_kernel.cu   # 2D OS-CFAR
│   │   └── peak_detect_kernel.cu  # NMS
│   └── utils.cu
├── apps/
│   ├── test_pipeline.cpp          # Standalone test
│   └── gnuradio_block.cpp         # OOT integration
├── scripts/
│   ├── profile.sh                 # Nsight profiling
│   └── generate_test_data.py      # Synthetic ELRS
└── docs/
    └── PERFORMANCE.md             # Benchmarks
```

## Ключові оптимізації
- **CUDA_CHECK / CUDA_KERNEL_CHECK** макроси для error handling
- Pinned memory для CPU→GPU transfers
- cuFFT plans pre-allocated
- Shared memory tiling у CFAR kernel
- Async streams для overlap STFT/CFAR/peak
- Bitonic sort або approximate rank для OS-CFAR
- NMS замість full connected components

## Цільові метрики
- ≥100 MS/s sustained
- p95 ≤ 10 ms
- 0 dropped samples (на RTX 3070)

## Залежності
- Реалізує аналіз [[17-gpu-stft-cfar-analysis]]
- Заміняє/розширює [[08-stage1-oscfar-cpp]]
- Інтегрується через [[07-oot-gnuradio-skeleton]]
- Цільовий компонент [[06-tz5-hybrid-pipeline]] Stage 1
