---
tags: [external, KB-extra, group-6, github, gnuradio, cuda, oot-module]
created: 2026-05-28
type: github
stage: 1
source_url: https://github.com/gnuradio/gr-cuda
status: done
language: C++/CUDA
gr_version: 3.10+
---

# gnuradio/gr-cuda — CUDA Support для GNU Radio

## Опис
**Офіційний OOT-модуль gnuradio organization** для CUDA-acceleration через custom buffer changes введені у GR 3.10. Блоки можуть processing data **прямо в GPU memory**, оминаючи host↔device transfers у `work()`.

## Ключова інновація
- GR 3.10 додав custom buffer system
- gr-cuda використовує його щоб блоки маніпулювали GPU-buffer без cudaMemcpy
- Це **точно те що треба нашому Stage 1** для 100 MS/s

## Acceleration пример
- `multiply_const` (демонстраційний)
- Production-ready blocks не специфіковані в README

## Build requirements
- NVIDIA CUDA-capable GPU
- CUDA toolkit
- **GR ≥ 3.10.0.0** (наша версія 3.10.11 ✓)
- CMake з CUDA language support

## Acknowledgments
- Black Lynx, Inc. (gr-cuda_buffer)
- David Sorber (custom buffer development)

## Релевантність
- **КРИТИЧНО для Stage 1**: точно той framework, на який треба будувати [[08-stage1-oscfar-cpp]]
- Замість самопису custom buffer для C++ блоку — взяти gr-cuda як base
- 0 dropped samples при 100 MS/s стає реальним коли STFT → CFAR → peak все на GPU без cudaMemcpy
- TODO: перевірити status (alpha/beta) і ліцензію перед integration

## Посилання
- [[07-oot-gnuradio-skeleton]]
- [[08-stage1-oscfar-cpp]]
- [[19-full-cuda-cpp-pipeline]]
- [[ext-cuda-gpu-22]] — shared memory патерни всередині kernel
