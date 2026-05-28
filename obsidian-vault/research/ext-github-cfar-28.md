---
tags: [external, KB-extra, group-5, github, cfar, matlab, sfnd, hybrid]
created: 2026-05-28
type: github
stage: 1
source_url: https://github.com/Swaroopainapurapu/Radar_2D_CFAR
status: done
language: MATLAB
---

# Swaroopainapurapu/Radar_2D_CFAR

## Опис
Sensor Fusion Nanodegree рішення — 2D CFAR для FMCW. **Гібрид CA + OS-CFAR** (claim from README).

## Параметри
- Training cells: **Tr=14, Td=6**
- Guard cells: **Gr=6, Gd=3**
- SNR offset: **6 dB**

## Алгоритм
- 2D FFT генерує range-Doppler map
- Sliding CUT по matrix
- Threshold з training cells statistics
- Compare signal vs threshold

## License
Не вказано

## Релевантність
- **Stage 1**: гібрид CA+OS — можлива альтернатива чистому OS
- **Параметри для початкового tuning**: Tr=14/Td=6, Gr=6/Gd=3, offset=6 dB → стартова точка для нашого CFAR
- Менший offset (6 dB) — більш чутливо, але вище FAR

## Посилання
- [[ext-github-cfar-26]]
- [[ext-github-cfar-29]], [[ext-github-cfar-30]], [[ext-github-cfar-31]]
- [[ext-cfar-theory-06]] — MSS-CFAR теж sort-free
