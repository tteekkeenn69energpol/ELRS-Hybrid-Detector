---
tags: [presentation, external, pdf, drone-detection, sdr, fpga, ism-band, flak]
created: 2026-05-28
type: presentation
stage: all
status: reference
drive_id: 1nLASQIT6VD51hQ_i1f8kVguNp5zeb9Yb
source: Drone_Detection_Sensor_with_Continuous_24_GHz_ISM_.pdf
authors: Przemysław Flak
venue: IEEE Access
year: 2021
pages: 13
doi: "10.1109/ACCESS.2021.3104738"
---

# Drone Detection Sensor з continuous 2.4 GHz ISM band coverage (SDR+FPGA)

## Цитування
Flak P. *Drone detection sensor with continuous 2.4 GHz ISM band coverage based on cost-effective SDR platform.* IEEE Access, 2021. DOI 10.1109/ACCESS.2021.3104738.
Silesian University of Technology, Gliwice, Poland.

## Релевантність для проєкту
**Прямий аналог архітектурі** SDR+FPGA для drone detection. Хоча працює на 2.4 GHz (не 915 MHz), методологія HW signal processing chain — однакова.

## Ключові ідеї
- **Покриття 2.400-2.483 GHz** (вся ISM band 2.4) — на відміну від типових SDR з 40 MHz instantaneous BW
- Спирається на **passive RF imaging techniques**
- **SDR + FPGA** для подолання 40 MHz обмеження popular SDRs
- **Hardware realization of signal processing chain** → мінімізує throughput SDR↔companion PC і офлоадить software computations
- Low-cost COTS components
- Валідовано lab + real-life
- Sensitivity reduction vs reference receiver — задокументована, узгоджена з HW специфікаціями
- Розглядається як sensor для ML датасетів + частина anti-drone системи

## Що взяти у наш pipeline
1. **HW offload pattern**: FPGA обробляє великий потік, host PC отримує "звужений" data → точно те що пропонує [[12-adrv9009-artix7-migration]]
2. Структура signal processing chain (energy detection → frame extraction → host) — релевантна для нашого CFAR-як-trigger підходу
3. Методологія верифікації lab + field
4. Бюджет sensitivity — vs наша вимога SNR -12 dB

## Залежності
- Архітектурний референс для [[12-adrv9009-artix7-migration]]
- Підтверджує підхід [[07-oot-gnuradio-skeleton]] (HW для Stage 1)
- Передує [[23-flak-czyba-distributed-sensor-grid]] (наступна робота того ж автора)
