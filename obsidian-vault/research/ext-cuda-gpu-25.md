---
tags: [external, KB-extra, group-4, nvidia, pva, cfar, jetson-orin, hw-accelerator]
created: 2026-05-28
type: docs
stage: 1-edge
source_url: https://docs.nvidia.com/pva/solutions/0.4.0/solutions-apis/group__PVA__OPERATOR__ALGORITHM__RADAR__CFAR.html
status: done
---

# NVIDIA PVA RadarCFAR API

## Що таке PVA
**Programmable Vision Accelerator** — спеціалізований compute platform NVIDIA для vision + radar на edge devices (Jetson, DriveOS).

## Підтримувані CFAR
- **PVA_CFAR_CA** (Cell Averaging) — поки що єдиний документований

## API
```c
pvaRadarCFARCreate(...);   // init operator instance
pvaRadarCFARSubmit(...);   // execute (CUDA + cuPVA streams)
```

## Input constraints
- 2D/3D tensors з magnitude (single channel)
- Width/height: **1-1024, divisible by 8**
- Data: **32-bit signed/unsigned integers only**

## Output
- Detection list з range/Doppler indices
- **Max 8192 detections**

## Target platforms
- Jetpack 7
- DriveOS 7
- x86 emulation

## Релевантність
- **Edge deployment** ([[16-edge-ai-fhss-tracker]]): Jetson Orin Nano CAN використовувати PVA замість GPU/CPU для Stage 1 → free GPU для Stage 4 NN
- Тільки CA-CFAR — для нашого OS-CFAR треба було б hybrid: PVA для CA-rough + GPU для OS-refine
- 1024 size constraint — наш fft_size 2048-4096 виходить за межі, треба tile або downsample

## Обмеження для нас
- Тільки INT32 input → потрібен quantize float|·|² → int з нашого STFT
- Max 8192 detections — більш ніж достатньо
- 8-divisible — easy alignment

## Посилання
- [[16-edge-ai-fhss-tracker]] — edge deployment план
- [[12-adrv9009-artix7-migration]] — альтернатива для field
- [[19-full-cuda-cpp-pipeline]] — host GPU варіант
