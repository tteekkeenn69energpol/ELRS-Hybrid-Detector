---
tags: [external, KB-extra, group-4, cuda, profiling, nersc, hpc, workflow]
created: 2026-05-28
type: docs
stage: 1
source_url: https://docs.nersc.gov/tools/performance/nvidiaproftools/
status: done
---

# NERSC — NVIDIA Profiling Tools на HPC

## Tools
- **Nsight Systems** — system-wide timeline
- **Nsight Compute** — kernel-level analysis

## Команди
### Nsight Systems
```bash
srun nsys profile --stats=true -t nvtx,cuda <code>
```

### Nsight Compute
```bash
dcgmi profile --pause      # пауза DCGM
ncu --kernel-id :::1 -o report_name <program>
dcgmi profile --resume
```

## Workflow tips
- Use `$SCRATCH` для analyses
- Match profiler versions local ↔ HPC
- **NVTX ranges** для секцій коду (типу `gr::tag_t`-аналог)
- Monitor host-device transfers
- `-set full` flag для roofline plots
- `.nsys-rep` / `.ncu-rep` файли — view локально через GUI

## Релевантність
- Готові команди для нашого `scripts/profile.sh` ([[19-full-cuda-cpp-pipeline]])
- NVTX ranges варто додати у наш Stage 1 kernel (markers per phase: STFT, magnitude, CFAR, peak)
- Roofline plot — спосіб довести что ми memory-bound у STFT 87.5% overlap (як попереджав [[17-gpu-stft-cfar-analysis]])

## Посилання
- [[ext-cuda-gpu-18]], [[ext-cuda-gpu-19]]
- [[19-full-cuda-cpp-pipeline]] — profile.sh має бути на цьому patternі
