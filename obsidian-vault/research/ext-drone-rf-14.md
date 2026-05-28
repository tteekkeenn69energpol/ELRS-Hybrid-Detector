---
tags: [external, KB-extra, group-3, cfar, sea-clutter, alpha-stable, fox-h-function]
created: 2026-05-28
type: paper
stage: 1
source_url: https://www.mdpi.com/2072-4292/12/8/1273
status: done
authors: Liu Xu, Xu Shuwen, Tang Shiyang
venue: MDPI Remote Sensing
year: 2020
volume: 12
issue: 8
doi: "10.3390/rs12081273"
---

# CFAR Strategy in Positive Alpha-Stable Sea Clutter (Fox's H-function)

## Цитування
Liu X., Xu S., Tang S. *CFAR Strategy Formulation and Evaluation Based on Fox's H-function in Positive Alpha-Stable Sea Clutter.* Remote Sensing, 2020, 12(8), 1273. DOI 10.3390/rs12081273.

## Короткий зміст
Target detection у **impulsive non-Gaussian sea clutter**. Positive α-stable (PαS) distribution — підтверджена модель для такого clutter, але **PDF не має closed form**. Стаття використовує **Fox's H-function** для представлення PDF і будує CFAR детектори (GO, SO, OS, CML) для PαS clutter.

## Ключові ідеї
- **Fox's H-function**: representation PDF для α-stable variables (інакше — Levy / Pareto-like)
- Перетворює analytically inexpressible cumulative density → tractable form
- Аналіз GO-CFAR, SO-CFAR, OS-CFAR, Censored Mean Level (CML) у PαS clutter
- Performance comparison залежно від α (heavy-tail parameter)

## Релевантність до проєкту
- **Stage 1**: коли ELRS spectrum має **impulsive interference** (бурсти WiFi, ESD spikes), Gaussian-припущення CFAR падає
- α-stable модель може бути ближча до правди для real-world ELRS spectrum
- CML detector як альтернатива OS-CFAR для heavy-tail noise
- Pure DSP-theory paper — можна піднімати при tuning false-alarm у польових випробуваннях

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[ext-drone-rf-13]] — теж adaptive radar CFAR
- [[ext-cfar-theory-08]] — Wilcoxon non-param (теж для heavy-tail)
