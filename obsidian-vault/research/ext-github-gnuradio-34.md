---
tags: [external, KB-extra, group-6, github, gist, cfar, pytorch, rust]
created: 2026-05-28
type: gist
stage: 1
source_url: https://gist.github.com/juhasch/eeb05b25085fc644fcdd1002770486e8
status: done
language: Python (PyTorch) + Rust (ndarray)
---

# juhasch CFAR gist — PyTorch + Rust

## Опис
Compact educational guide implementuючий **CFAR** у двох мовах:
- **Python (PyTorch)** з `torch.nn.functional.unfold`
- **Rust (ndarray)** з manual window iteration

## Ключова техніка (PyTorch)
- `torch.nn.functional.unfold` ефективно витягує sliding windows
- Compute dynamic threshold від surrounding noise
- Vectorized — GPU-friendly через PyTorch CUDA

## Rust (CPU)
- `ndarray` crate
- Manual window iteration без GPU
- Same algorithm, без acceleration

## Core concept (обидві імплементації)
1. Extract sliding window neighborhood навколо CUT
2. Calculate mean noise level
3. Sensitivity multiplier → dynamic threshold
4. Compare CUT vs threshold

## Релевантність
- **PyTorch CFAR**: цікаво для **fine-tuning Stage 4 neural verifier** — CFAR-as-differentiable-layer ([[ext-cfar-theory-05]] CFARnet)
- `unfold` як Pythonic alternative до raw CUDA — потенційно для Stage 2 если CuPy недостатньо
- **Rust** — варіант для embedded standalone CLI tools (без GPU)
- На відміну від MATLAB/SFND варіантів ([[ext-github-cfar-26]] etc), це Python+Rust → ближче до нашого стеку

## Не SDR-related
Note з аналізу: цей gist — pure radar CFAR algorithm, **не GNU Radio block**. Опинився у Group 6 (GR/SDR) випадково за нашою класифікацією — насправді ближче до Group 1/5.

## Посилання
- [[ext-cfar-theory-05]] — CFARnet (NN з CFAR constraint)
- [[ext-github-cfar-26]] до [[ext-github-cfar-31]] — інші CFAR repos
- [[ext-cuda-gpu-24]] — Numba CUDA для Python kernels
