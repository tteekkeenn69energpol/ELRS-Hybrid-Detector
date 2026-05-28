---
tags: [external, KB-extra, group-5, github, cuda, convolution, gpu, astroaccelerate]
created: 2026-05-28
type: github
stage: 1
source_url: https://github.com/KAdamek/GPU_Overlap-and-save_convolution
status: done
language: CUDA C++
---

# KAdamek/GPU_Overlap-and-save_convolution

## Опис
**CUDA C++ implementation overlap-and-save convolution** для signal processing. Походить з AstroAccelerate (radio astronomy). Дві реалізації: cuFFT-based та **shared-memory FFT** (всі OLS-кроки в одному kernel).

## Що робить
Overlap-and-save розбиває long signal на segments, які обробляються незалежно — ефективна linear convolution для long signal + short filter. Класична задача DSP.

## Ключові оптимізації
- cuFFT варіант (baseline)
- **Shared-memory FFT варіант**: усі OLS-кроки в **одному CUDA kernel** → без device memory transactions між стадіями
- Це pattern, який ми ховаємо у [[19-full-cuda-cpp-pipeline]]: fused kernel замість stage-by-stage

## Benchmarks
- **до 2.5× speedup** complex-to-complex (257-sample filters)
- **до 4× speedup** real-to-real
- vs стандартний підхід

## License
LICENSE файл існує в repo (README placeholder "[insert license]"). Перевірити перед використанням коду.

## Релевантність
- **Stage 1 / Stage 3**: matched filtering для preamble detection — це convolution. OLS на GPU = точно те що треба для Dechirp/MF на high samp_rate
- **Fused kernel pattern**: argumentum для нашого fused STFT+|·|²+CFAR kernel у [[19-full-cuda-cpp-pipeline]]
- **AstroAccelerate** — близька галузь (FRB detection ≈ chirp detection!)

## Посилання
- [[02-tz1-dechirp-mf]] — наш matched filter
- [[19-full-cuda-cpp-pipeline]] — fused kernel pattern
- [[25-venter-sdr-pulse-doppler-gpu]] — DPC через FFT-based convolution
- [[ext-cuda-gpu-22]] — NVIDIA Shared Memory blog (теоретична база)
