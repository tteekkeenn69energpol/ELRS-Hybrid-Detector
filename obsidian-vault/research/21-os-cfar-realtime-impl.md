---
tags: [presentation, external, pdf, oscfar, cfar, fpga, gpu, realtime, sorting]
created: 2026-05-28
type: presentation
stage: 1
status: reference
drive_id: 1Hwuchmjkz1bzE0DhLbiEAvOKcC-1X0KV
source: article.pdf
authors: Bales, Benson, Dickerson, Campbell, Hersey, Culpepper
venue: Georgia Tech Research Institute / AFRL
pages: 6
---

# Real-Time Implementations of Ordered-Statistic CFAR

## Цитування
Bales M.R., Benson T., Dickerson R., Campbell D., Hersey R., Culpepper E.
*Real-Time Implementations of Ordered-Statistic CFAR.*
Sensors and Electromagnetic Applications Laboratory, Georgia Tech Research Institute & AFRL.

## Релевантність для проєкту
**Прямий референс для Stage 1** ([[06-tz5-hybrid-pipeline]], [[08-stage1-oscfar-cpp]], [[19-full-cuda-cpp-pipeline]]).

## Ключові ідеї
- **OS-CFAR vs CA-CFAR**:
  - CA-CFAR: arithmetic mean → ML estimate, але потребує homogeneous training
  - OS-CFAR: rank-order training data → robust на multiple targets / heterogeneous clutter
  - Ціна: O(N²) brute force замість O(N) для CA
- **Реальні архітектури**:
  - FPGA з novel sorting architecture, що **масштабується лінійно з window size**
  - FPGA compare-and-swap та rank-only варіанти
  - GPU rank-only implementation
  - CPU multi-threaded sorting + rank-only
- **Аналіз**: throughput і power consumption vs training window size

## Що взяти у наш pipeline
1. **Rank-only підхід** для OS-CFAR — не сортувати всі точки, тільки знайти k-ту порядкову
2. Готова FPGA архітектура з лінійним scaling → для [[12-adrv9009-artix7-migration]]
3. Бенчмарки throughput/power → референс для наших цільових метрик 100 MS/s
4. Питання training window size → впливає на False Alarm Rate і обчислювальну вартість

## Залежності
- Прямий референс [[08-stage1-oscfar-cpp]]
- Прямий референс [[19-full-cuda-cpp-pipeline]]
- Обговорено в [[17-gpu-stft-cfar-analysis]] (там підказано "approximate rank via histogram")
- HW варіант для [[12-adrv9009-artix7-migration]]
