---
tags: [external, KB-extra, group-4, cuda, profiling, tutorial]
created: 2026-05-28
type: tutorial
stage: 1
source_url: https://ajdillhoff.github.io/notes/profiling_cuda_applications/
status: done
---

# Profiling CUDA Applications (Dillhoff notes)

## Tool
NVIDIA NSight Compute (`ncu ./build/main`)

## Key metrics to monitor
- **Duration** — total kernel time (главне)
- **SM Throughput [%]** — SM utilization vs peak
- **Memory Throughput [%]** — memory subsystem vs theoretical max

## Важливі секції в звіті
- **GPU Speed of Light** — high-level bottleneck overview
- **Launch Statistics** — grid/block config + resources per block
- **Occupancy Analysis** — theoretical vs achieved occupancy

## Optimization framework (cyclic)
```
Profile → Identify bottleneck → Inspect code → Optimize → Profile
```
Спочатку зрозуміти: memory-bound чи compute-bound. Strategy різна.

## Pitfalls
- **High throughput % ≠ high performance** (можна виконувати багато непотрібного)
- Larger grids → overhead, може зменшити performance

## Релевантність
- Practical-style рецепти для onboarding нових розробників на наш проєкт
- Confirms `Memory-bound vs compute-bound` triage що ми робимо в [[17-gpu-stft-cfar-analysis]]

## Посилання
- [[ext-cuda-gpu-18]], [[ext-cuda-gpu-19]], [[ext-cuda-gpu-20]]
- [[19-full-cuda-cpp-pipeline]] — PERFORMANCE.md може спиратись на цей checklist
