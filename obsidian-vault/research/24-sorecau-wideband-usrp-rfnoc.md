---
tags: [presentation, external, pdf, drone-detection, usrp, rfnoc, gnuradio, fosphor, mdpi]
created: 2026-05-28
type: presentation
stage: all
status: reference
drive_id: 11Kp5IRCT7xcuG0L5KEC5twERFGjjVfuZ
source: drones-10-00117.pdf
authors: Sorecău M., Sorecău E., Bechet P.
venue: MDPI Drones
year: 2026
pages: 37
doi: "10.3390/drones10020117"
---

# Wideband Monitoring System of Drone Emissions (USRP + RFNoC)

## Цитування
Sorecău M., Sorecău E., Bechet P. *Wideband Monitoring System of Drone Emissions Based on SDR Technology with RFNoC Architecture.* Drones, 2026, 10(2), 117. DOI 10.3390/drones10020117.
Nicolae Bălcescu Land Forces Academy (Sibiu), Cluj-Napoca Technical University, Robetech EMC.

## Релевантність для проєкту
**Найсвіжіший (Feb 2026) і найповніший** реферат на multi-channel SDR + GNU Radio + GPU spectrograms для drone monitoring. Релевантно для нашої roadmap масштабування і вибору HW.

## Ключові цифри
- **Sensitivity: -130 dBm** (перевершує літературу)
- **>200 MHz cumulative bandwidth** (два broadband 160+80 MHz + один narrow 1 MHz @ 2437 MHz)
- 2.4 та 5.8 GHz ISM bands
- **RFNoC** (RF Network-on-Chip) — DSP офлоад на FPGA USRP
- **GPU-accelerated спектрограми** (Fosphor)
- Live візуалізація з persistent display
- **OpenDroneID decoding** (RDID детекція)
- Динамічний band switching, multiple simultaneous drones

## Архітектура
- USRP X-series з 3 каналами (2 broadband + 1 narrow)
- Optical fiber для transport (low loss)
- High-perf CPU + fast storage + GPU
- GNU Radio + RFNoC + custom blocks
- FFT/filtering на FPGA (latency-критично)
- Persistent spectrogram на GPU (Fosphor)

## Що взяти у наш pipeline
1. **>200 MHz**: альтернатива ADRV9009 — multi-channel USRP X-series + RFNoC ([[12-adrv9009-artix7-migration]])
2. **Fosphor** — GPU persistent spectrograms для GUI (можна вкласти в наш Waterfall display)
3. **OpenDroneID** — стандартний remote ID протокол → додатковий канал детекції (не ELRS, але корисно)
4. **-130 dBm sensitivity bar** — target для нашого Aaronia/ADRV9009 setup
5. **RFNoC pattern** — DSP офлоад на USRP FPGA замість host CPU/GPU

## Залежності
- Альтернатива HW для [[12-adrv9009-artix7-migration]]
- GUI/visualization референс для [[10-gnuradio-flowgraph]]
- Multi-band підхід — конкурент [[14-commercial-defence-analysis]] таблиці
