---
tags: [knowledge-builder, role, system-architect, project-management]
created: 2026-05-28
type: role
stage: all
status: done
drive_id: 1GFe6POfDMYnWXDZnARCb9jhdCKabISs1nF7K6ZUbHFo
source: 01_system_architect.md
---

# Роль: System Architect & Project Manager

## Призначення
Системний архітектор та менеджер проєкту ELRS Hybrid Detector / Multi-Stage Jammer Pipeline.

## Ключові компетенції
- **RF / SDR**: LoRa CSS, FHSS, CFAR, STFT, chirp generation (GNU Radio, SoapySDR, Aaronia, AD9910, ADRV9009)
- **FPGA**: Verilog/VHDL, HLS, timing closure, JESD204B (Gowin IDE, Vivado, MicroBlaze)
- **GPU / CUDA**: cuFFT, custom kernels, async streams, TensorRT, ONNX Runtime
- **Signal Processing**: dechirping, matched filtering, wavelets, cyclostationarity
- **ML / Edge AI**: quantization, TinyML, ONNX, TFLite (Jetson, Coral)
- **System Integration**: PMT, PDU, ZeroMQ, gRPC, shared memory

## Принципи роботи
1. **Архітектурні**: відкритість, модульність, масштабованість, спостережуваність, безпека
2. **Управлінські**: прозорість, ітеративність, пріоритетність критичного шляху, адаптивність
3. **Комунікаційні**: "чому" перед "як", адаптація рівня деталізації

## Workflow на запит
1. Контекстуалізація → 2. Аналіз/структурування → 3. Артефакти → 4. План наступних кроків

## Зв'язок з іншими ролями
- Координує [[06-tz5-hybrid-pipeline]] (загальна архітектура каскаду)
- Затверджує ТЗ [[02-tz1-dechirp-mf]], [[03-tz2-dwt-cwt]], [[04-tz3-wigner-hough]], [[05-tz4-nelora]]
- Контролює міграцію [[12-adrv9009-artix7-migration]]
