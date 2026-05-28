---
tags: [external, KB-extra, group-1, cfar, matlab, reference, docs]
created: 2026-05-28
type: docs
stage: 1
source_url: https://www.mathworks.com/help/phased/ref/2dcfardetector.html
status: done
---

# MATLAB 2-D CFAR Detector (Phased Array System Toolbox)

## Короткий зміст
Simulink-блок для 2D CFAR детекції в image-data (range-Doppler matrices, spectrograms). Видає detection якщо cell-under-test перевищує адаптивний поріг, обчислений з training cells.

## Підтримувані методи
- **CA** (Cell-Averaging) — mean всіх training cells
- **GOCA** (Greatest-Of) — більше з left/right half means
- **SOCA** (Smallest-Of) — менше з halves
- **OS** (Order Statistic) — k-та порядкова з sorted training cells

## Ключові параметри
- `NumGuardCells` — guard band довкола CUT
- `NumTrainingCells` — training band
- `ThresholdFactor` — multiplier на noise estimate (auto з Pfa або custom)

## Релевантність до проєкту
- **Stage 1**: референс API і параметризації для нашого блоку
- Корисно для **прототипування на MATLAB** перед C++/CUDA реалізацією: можна валідувати алгоритм + ground truth
- 4 методи (CA/GOCA/SOCA/OS) — той самий пул, що ми розглядаємо для нашого детектора

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[19-full-cuda-cpp-pipeline]]
- [[21-os-cfar-realtime-impl]] — real-time реалізації OS-CFAR
