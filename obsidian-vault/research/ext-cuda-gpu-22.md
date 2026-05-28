---
tags: [external, KB-extra, group-4, cuda, shared-memory, nvidia-blog, optimization]
created: 2026-05-28
type: tutorial
stage: 1
source_url: https://developer.nvidia.com/blog/using-shared-memory-cuda-cc/
status: done
---

# Using Shared Memory in CUDA C/C++ (NVIDIA blog)

## Ключові факти
- **Shared memory** = on-chip, ~100× нижча latency, ніж uncached global
- Allocated **per thread block** — threads cooperate / share data
- Race conditions без `__syncthreads()` barrier

## Declaration
- **Static**: fixed-size compile-time array
- **Dynamic**: `extern` unsized array, size передається через третій параметр у `<<<grid, block, sharedBytes>>>`

## Bank conflicts
- Shared memory ділиться на **banks**
- Кілька threads → один bank = **serialized access** (×N slowdown)
- Devices: 16 banks (1.x), **32 banks (2.0+)**

## Synchronization
```cuda
__syncthreads();   // all threads of block must reach
```

## Pattern в blog
Array reversal через shared memory для coalesced global reads — класична демонстрація.

## Релевантність
- **Stage 1 CFAR**: tiled shared-memory loading — головна оптимізація (див. [[25-venter-sdr-pulse-doppler-gpu]] про partition camping)
- **STFT**: shared memory для window function + FFT data ([[ext-github-cfar-27]])
- **32 banks для cap = 2.0+**: наша RTX 3070 (cap 8.6) — 32 banks → треба перевіряти conflict patterns на 32-wide warp

## Посилання
- [[ext-lora-detection-11]] — CERN sliding window — практичний приклад
- [[ext-github-cfar-27]] — KAdamek OLS convolution з shared memory
- [[19-full-cuda-cpp-pipeline]]
- [[25-venter-sdr-pulse-doppler-gpu]] — partition camping, corner turning
