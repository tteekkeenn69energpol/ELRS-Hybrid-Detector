---
tags: [external, KB-extra, group-5, github, cfar, matlab, sfnd]
created: 2026-05-28
type: github
stage: 1
source_url: https://github.com/stevenliu216/SFND_Radar_Target_Generation_and_Detection
status: done
language: MATLAB
---

# stevenliu216/SFND_Radar_Target_Generation_and_Detection

## Опис
Udacity SFND capstone — 2D CFAR на range-Doppler matrix.

## Параметри (примітно більші у Doppler-осі)
- Training: **Tr=12, Td=28**
- Guard: **Gr=4, Gd=8**
- Offset: **15.5 dB**

Більші Td/Gd через **вищу шумову варіацію в Doppler-axis**.

## CFAR variant
Sliding CUT, exclude guard, threshold from training, apply offset.

## License
Не вказано

## Релевантність
- **Корисний інсайт**: asymmetric training/guard window (Tr ≠ Td) — для axis з різною noise variance
- У нашому case (час vs частота) — час може мати більший noise variance через bursty interferers → варто експериментувати з asymmetric window
- Offset 15.5 dB — консервативно, низький FAR

## Посилання
- [[ext-github-cfar-26]], [[ext-github-cfar-28]], [[ext-github-cfar-29]], [[ext-github-cfar-31]]
