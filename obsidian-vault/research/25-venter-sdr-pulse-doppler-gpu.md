---
tags: [presentation, external, pdf, thesis, cuda, gpgpu, radar, cfar, fft, optimization]
created: 2026-05-28
type: presentation
stage: 1
status: reference
drive_id: 1i-EH6kBXCW5IVX_y6OV1pZGEfMZ5C1Mp
source: Venter_Software_2014.pdf
authors: Christian Jacobus Venter (supervisor H. Grobler)
venue: U. of Pretoria, MEng thesis
year: 2014
pages: 166
---

# Software-Defined Pulse-Doppler Radar Signal Processing on GPUs (MEng thesis)

## Цитування
Venter C.J. *Software-Defined Pulse-Doppler Radar Signal Processing on Graphics Processors.* Master of Engineering thesis, University of Pretoria, May 2014.
Supervisor: Mr. H. Grobler.

## Релевантність для проєкту
**Енциклопедичний референс по GPGPU оптимізації** для радарного DSP pipeline (DPC + CT + DF + ENV + CFAR). 166 сторінок методології, мікробенчмарків і реальних оптимізацій. Прямий вхід для [[19-full-cuda-cpp-pipeline]] і [[17-gpu-stft-cfar-analysis]].

## Платформа
- NVIDIA Tesla C1060 + CUDA (single-precision FP)
- Coherent pulse-Doppler радар, single receiver-element
- 2D data storage model

## Контекст обчислень
- First-stage data-independent processing: **1 Gop/s – 1 Top/s**
- FIR filters, correlation, FFT, matrix-vector algebra на multi-dim data
- Hundreds of GB/s memory bandwidth GPU
- Several Tflops single-chip

## Ключові висновки (бенчмарки + рекомендації)
1. **Severity of uncoalesced device memory access** — pattern memory access критично для throughput
2. **Arithmetic intensity** має бути високою (інакше memory-bound)
3. **Asymmetry в primitive math ops** — деякі операції набагато дорожчі
4. **Memory transfer для small buffers** — фундаментально повільний; **transfer overlap з computation** ефективний
5. **DPC та DF**: FFT-based варіанти через CUFFT — оптимальні
6. **Corner Turning**: shared memory обов'язково для coalesced; **partition camping** — небезпечний side-effect
7. **CFAR**: сегментація на окремі стадії для рядків і стовпців — найважливіша оптимізація
8. **ENV + helper kernels** (padding, scaling, windowing) — bandwidth-limited; як `cudaMemcpy` за швидкістю

## Що взяти у наш pipeline
1. **CFAR row/column segmentation** — пряма архітектурна рекомендація для нашого 2D OS-CFAR ([[19-full-cuda-cpp-pipeline]])
2. **CUFFT для STFT** — підтвердження вибору ([[17-gpu-stft-cfar-analysis]])
3. **Partition camping** уникати при corner-turning — релевантно для transpose між STFT і CFAR
4. **Transfer overlap з compute** через streams — наш підхід для 100 MS/s
5. **Microbenchmark методологія** — взяти для нашого PERFORMANCE.md
6. Окремий розділ thesis по analytical performance framework — корисно для модулювання limitations

## Залежності
- Методологічна база для [[19-full-cuda-cpp-pipeline]]
- Підтверджує підхід [[17-gpu-stft-cfar-analysis]]
- Корисно для бенчмарків Stage 1 [[08-stage1-oscfar-cpp]]
- Старіше (2014, Tesla C1060) — для RTX 3070 деякі цифри змінилися, але архітектурні рекомендації досі чинні
