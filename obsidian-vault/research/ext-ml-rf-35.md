---
tags: [external, KB-extra, group-7, company, sdr, air-t, deepwave]
created: 2026-05-28
type: tool
stage: all
source_url: https://deepwave.ai/
status: done
---

# DeepWave AI — RF + AI platform

## Опис
Компанія DeepWave перетворює RF сигнали на real-time intelligence. Tagline: "RF Data Into Real-Time Insights." Поєднує software stack + dedicated hardware.

## Продукти

### AirStack Software Suite
- Edge / Core / BitStream варіанти
- Управляє AI + signal processing через edge HW + RF platforms

### AIR-T Hardware
- **Software-defined radios** спеціально для RF + wireless deep learning
- Edge / Embedded / Flight Series
- FPGA acceleration + ML

## Технологія
Low-latency RF → intelligence для автоматичних systems. FPGA + ML combo.

## Цільові ринки
- Avionics + airspace navigation
- Autonomous vehicles
- Industrial IoT (manufacturing, logistics)
- 5G/6G
- Electronics product dev
- **Defense** (F-16 fleet enhancement згадано)

## Релевантність до проєкту
- **AIR-T** — пряма альтернатива нашому SoapySDR+Aaronia / ADRV9009+Artix-7 setup
- "FPGA + ML" — точно наш паттерн (Stage 1 на FPGA, Stage 4 NN на host)
- Defense customer base (F-16) — підтверджує комерційний попит на цей вид tooling
- **AirStack** як концепт unified RF+AI stack — натхнення для нашого UnifiedConfiguration
- TODO: перевірити чи AIR-T має 100 MS/s + 200 MHz BW, conv опорна точка з ADRV9009

## Посилання
- [[12-adrv9009-artix7-migration]] — наша HW альтернатива
- [[14-commercial-defence-analysis]] — competitive landscape
- [[16-edge-ai-fhss-tracker]] — edge AI deployment паттерн
