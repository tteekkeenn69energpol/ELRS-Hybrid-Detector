---
tags: [knowledge-builder, hardware, fpga, adrv9009, artix7, jesd204b, migration]
created: 2026-05-28
type: tz
stage: 1-hw
status: planned
drive_id: 1s6bP-NMZByLtlLl08JObciV-noa4aTlVfaYOe8Is4-U
source: 12_adrv9009_artix7_migration.md
---

# Міграція на ADRV9009 + Artix-7 A7-Lite

## Призначення
Перехід від лабораторного макету (SoapySDR + PC) до компактного embedded рішення.
ADRV9009: 200 MHz instantaneous bandwidth → детекція всього ELRS діапазону одночасно без сканування.

## Архітектура
```
RF Antenna
  → ADRV9009 Transceiver (200 MHz BW, 12-bit ADC)
  → JESD204B (4-8 lanes @ 3.125 Gbps)
  → Artix-7 A7-Lite FPGA:
       - JESD204B RX IP Core
       - AXIS FIFO
       - Stage 1: 2D OS-CFAR (HW Accel)
            - FFT IP (1024 pts)
            - CFAR Logic (Guard/Train cells)
       - Packetizer (UART / Ethernet / PCIe)
  → Host PC (тільки тригери):
       - Stage 2-4 (Python/CuPy, NN)
```

## Чому такий розподіл
- Artix-7 обмежений DSP → ідеальний для Stage 1 (швидкий потік, фільтрація)
- PC бере складну математику (wavelets, NN), отримуючи "підозрілі" ділянки

## План реалізації
1. **Тиждень 1-2**: ADRV9009 profile (TES → `profile.h`), hardware check (FMC, 122.88 MHz / 30.72 MHz reference)
2. **Тиждень 3-5**: ініціалізація ADRV9009 на A7 (рекомендовано: MicroBlaze + adrv9009_api від ADI)
3. **Тиждень 6-7**: JESD204B Link & RX path (Xilinx `JESD204B_RX` IP, Subclass 1, 16-bit)
4. **Тиждень 8-10**: Stage 1 HDL (FFT IP + CFAR HDL)
5. **Тиждень 11-12**: Packetizer + Host integration

## Ризики
- Artix-7 A7-Lite не має ARM ядра → потрібен MicroBlaze або No-OS driver
- Timing closure для JESD204B на A7 — складно
- DSP slices в A7 обмежені для повного CFAR

## Залежності
- Цільова форма для [[08-stage1-oscfar-cpp]]
- Замінює PC-only [[10-gnuradio-flowgraph]] у польовій версії
- Альтернатива Edge AI: [[16-edge-ai-fhss-tracker]]
