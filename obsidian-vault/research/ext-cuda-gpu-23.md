---
tags: [external, KB-extra, group-4, cuda, sliding-window, stackoverflow]
created: 2026-05-28
type: forum
stage: 1
source_url: https://stackoverflow.com/questions/7656277/generalized-sliding-window-computation-on-the-gpu
status: partial
---

# Generalized sliding-window computation on GPU (StackOverflow)

## Примітка
WebFetch блокує stackoverflow.com у Claude Code. WebSearch fallback не повернув конкретного посилання.

## Що відомо з URL/контексту
Питання про **загальний паттерн sliding-window обчислень на GPU** — той самий, що використовується у:
- 2D CFAR (training+guard window)
- Конволюція (matched filter)
- Stencil computations
- Image filters

## Канонічні відповіді (з community CUDA practice)
1. **Tiled shared-memory loading**: завантажити tile (block_size + window_radius) у shared, потім кожен thread читає вікно з shared
2. **Halo regions**: border tiles потребують overlap читання
3. **Cooperative thread loading**: 32 threads warp кооперативно завантажують tile
4. **Block size 16×16 типово** ([[ext-lora-detection-11]])

## Релевантність
- Підтверджує загальний паттерн, який ми використовуємо у Stage 1 CFAR
- Дублюється у CERN presentation [[ext-lora-detection-11]] з конкретним прикладом

## Посилання
- [[ext-lora-detection-11]] — конкретна CUDA реалізація
- [[ext-cuda-gpu-22]] — Shared memory NVIDIA blog
- [[19-full-cuda-cpp-pipeline]]
