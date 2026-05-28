---
tags: [external, KB-extra, group-4, cuda, nsight-compute, tool]
created: 2026-05-28
type: tool
stage: 1
source_url: https://developer.nvidia.com/nsight-compute
status: done
---

# NVIDIA Nsight Compute — продуктова сторінка

## Опис
Interactive профайлер CUDA + OptiX. Detailed metrics + API debugging, GUI + CLI.

## Що профайлить
- GPU compute kernels + hardware activity
- Memory workload + data transfer
- Source line-level performance correlation (з SASS і PTX)

## Ключові features
- **Guided analysis** з вбудованими NVIDIA-рекомендаціями
- **Memory heatmaps** для bottleneck visualization
- Source correlation (SASS/PTX)
- Interactive profiling + CUDA Graph exploration
- **NVRules API** для Python custom workflows

## Platforms
- Standalone або в CUDA Toolkit
- Local + remote profiling
- Multiple GPU архітектур

## Релевантність
- Tool, який ми ставимо як обов'язковий для всіх Stage 1 CUDA kernels
- Memory heatmaps допоможуть з coalescing issues ([[25-venter-sdr-pulse-doppler-gpu]])
- Source correlation важлива для tuning `os_cfar_2d_kernel.cu` line-by-line

## Посилання
- [[ext-cuda-gpu-18]] — Profiling Guide
- [[ext-cuda-gpu-20]] — NERSC workflow
- [[19-full-cuda-cpp-pipeline]]
