---
tags: [external, KB-extra, group-5, github, cfar, matlab, sfnd]
created: 2026-05-28
type: github
stage: 1
source_url: https://github.com/nbarendes/SFND_Radar_2D_CIFAR_Process
status: done
language: MATLAB
---

# nbarendes/SFND_Radar_2D_CIFAR_Process

## Опис
SFND варіант: FMCW radar simulation з 1D/2D FFT і adaptive thresholding.

## CFAR variant
**2D CA-CFAR** з ремаркою "combination of OS and CA CFAR" (рейн дизайн против multi-target masking + computational efficiency).

## Параметри
- Training: **Tr=10, Td=8**
- Guard: **Gr=4, Gd=4**

## License
Не вказано

## Релевантність
- Інша стартова комбінація параметрів — для свого test_pipeline.cpp бенчмарку
- "OS+CA combo" — підтверджує тренд гібридизації

## Посилання
- [[ext-github-cfar-26]], [[ext-github-cfar-28]], [[ext-github-cfar-30]], [[ext-github-cfar-31]]
