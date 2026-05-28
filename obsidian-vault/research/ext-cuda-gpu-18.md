---
tags: [external, KB-extra, group-4, cuda, profiling, nsight-compute, docs]
created: 2026-05-28
type: docs
stage: 1
source_url: https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
status: done
---

# NVIDIA Nsight Compute — Profiling Guide

## Що це
Профайлер для CUDA kernels: збирає GPU-метрики через кілька execution passes, перехоплює CUDA driver без зміни коду.

## Replay modes
- **Kernel** — saves/restores memory між passes
- **Application** — повний rerun
- **Range** — concurrent kernels

## Available metrics
- Occupancy
- Memory utilization
- SM throughput
- Warp stalls
- Cache efficiency
- Instruction-level execution
- Categorії: counters / ratios / throughputs (% peak)

## vs Nsight Systems
- **Nsight Systems**: trace concurrent execution (timeline view)
- **Nsight Compute**: serialize kernels for detailed metrics (might report different durations)

## Коли використовувати
- Bottleneck analysis on individual kernel
- Occupancy optimization
- Memory vs compute-bound identification

## Релевантність до проєкту
- **Stage 1**: профайлинг наших CFAR + STFT kernels для 100 MS/s target
- Метрики SM throughput / memory bandwidth скажуть якщо ми pinned-pinned-bandwidth-bound (як попереджає [[17-gpu-stft-cfar-analysis]])
- Mandatory tool для оптимізації [[19-full-cuda-cpp-pipeline]]

## Посилання
- [[ext-cuda-gpu-19]] — Nsight Compute product page
- [[ext-cuda-gpu-20]] — NERSC workflow
- [[ext-cuda-gpu-21]] — practical tutorial
- [[19-full-cuda-cpp-pipeline]] — наш scripts/profile.sh має використовувати ncu
