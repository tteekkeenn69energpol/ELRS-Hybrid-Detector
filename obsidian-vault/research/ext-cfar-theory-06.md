---
tags: [external, KB-extra, group-1, cfar, mss, novel-algorithm, paper]
created: 2026-05-28
type: paper
stage: 1
source_url: https://www.globalscientificjournal.com/researchpaper/A_Novel_Approach_for_Accurate_Target_Detection_in_the_worst_Radar_Environments.pdf
status: done
local_pdf: data/raw/pdf/06_novel_target_detection_worst_radar.pdf
authors: Mustafa Subhi Kamal
venue: Global Scientific Journal, Vol 11 Issue 6
year: 2023
pages: 5
---

# A Novel Approach for Accurate Target Detection in worst Radar Environments

## Цитування
Kamal M.S. *A Novel Approach for Accurate Target Detection in the worst Radar Environments.* GSJ Vol 11, Issue 6, June 2023. ISSN 2320-9186.
Electric Engineering Dept., Al Iraqiya University.

## Короткий зміст
Запропоновано метод **MSS-CFAR (Maximum Spike Subtraction)** для CFAR в радар-приймачах. Алгоритм вибирає maximum sample amplitude і **віднімає** його з суми echo-samples у sliding reference window → точніша noise estimate → нижчий FAR у multi-target + heavy clutter сценаріях.

## Алгоритм
1. Sliding reference window навколо CUT
2. Знайти max amplitude у window (successive sample comparison, без sorting/ranking)
3. Subtract max з sum-of-window → background estimate
4. Threshold = α · background_estimate
5. Compare CUT з threshold

## Перевага
- **Без сортування** (на відміну від OS-CFAR) → менша обчислювальна вартість, придатне для hardware
- **Робастно у multi-target within clutter clouds** — там де CA-CFAR падає (target masking), а OS-CFAR дорогий

## Порівняння (MATLAB simulation)
MSS-CFAR vs CA-CFAR vs OS-CFAR на MATLAB clutter test model для різних радарних сценаріїв. Деталі — у тексті PDF.

## Релевантність до проєкту
- **Stage 1**: можлива **дешевша альтернатива OS-CFAR** для FPGA (без sort)
- Compromise між CA (simple, fragile) і OS (robust, expensive)
- **Артикул**: для нашого ELRS pipeline з 2-3 одночасними передавачами — MSS може бути hardware-ефективніший
- TODO: побенчмаркати MSS у нашому test_pipeline.cpp

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[21-os-cfar-realtime-impl]] — порівняння HW реалізацій OS-CFAR
- [[ext-cfar-theory-03]] — варіанти CFAR
