---
tags: [external, KB-extra, group-2, cuda, sliding-window, cern, presentation]
created: 2026-05-28
type: presentation
stage: 1
source_url: https://indico.cern.ch/event/268353/contributions/1606636/attachments/480140/664100/pres20130420.pdf
status: done
local_pdf: data/raw/pdf/11_cern_2013_cuda.pdf
authors: Matthew Lockner
venue: CERN (indico event 268353)
year: 2013
pages: 27
---

# Two Applications Using CUDA — CERN 2013

## Цитування
Lockner M. *Two Applications Using CUDA* (sliding-window algorithm + pattern matching). CERN indico event 268353, presented August 20, 2013.

## Короткий зміст
CERN presentation з двома CUDA-додатками:
1. **Revised sliding-window algorithm** — shared memory + parallel reduction для max
2. **CUDA-based pattern-match/associative memory** — match string у array кандидатів

Дуже релевантне для нашого CFAR (теж sliding-window на 2D matrix → max).

## Ключові деталі sliding-window
- Goal: для матриці і window size — обчислити суми всіх windows + знайти max-sum window
- Test setup: **88×62 event array, 5×5 window**
- Layout:
  - **16×16 threads per block** (256, common sweet spot)
  - **Tile input у 16×16**, копія в shared memory
  - Кожен block рахує свої window sums + sub-result (max-sum локально)
  - Final max через **GPU parallel reduction**
- Parallel reduction замість CPU-side max (уникнення PCIe transfer)
- Один CUDA thread = один 5×5 window sum

## Чому це важливо для нашого Stage 1
2D OS-CFAR — це **точно sliding-window задача**: training+guard window перемішується по range-Doppler / time-freq matrix → шукати CUT vs threshold. Lockner показує саме ту layout-стратегію, яку рекомендує [[25-venter-sdr-pulse-doppler-gpu]] і яку ми застосуємо в [[19-full-cuda-cpp-pipeline]]:
- **Tiled shared-memory loading** для уникнення uncoalesced global reads
- **Block-local reductions** перед global
- **Parallel reduction** для top-k peaks (наш Peak Detection після CFAR)

## Релевантність до проєкту
- **Stage 1 CFAR**: прямий референс layout (16×16 threads, tile→shared, reduction-based max)
- **Peak detection** ([[19-full-cuda-cpp-pipeline]]): parallel reduction замість CPU
- Pattern-match (друга частина): корисно для **preamble correlation** на GPU (Stage 3)

## Посилання
- [[19-full-cuda-cpp-pipeline]]
- [[25-venter-sdr-pulse-doppler-gpu]] — теж sliding-window для CFAR
- [[ext-cuda-gpu-22]] — NVIDIA Shared Memory blog (group 4)
- [[ext-cuda-gpu-23]] — StackOverflow generalized sliding-window (group 4)
