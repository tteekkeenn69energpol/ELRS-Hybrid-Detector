---
tags: [external, KB-extra, group-5, github, cfar, matlab, fmcw]
created: 2026-05-28
type: github
stage: 1
source_url: https://github.com/BoJi07/Radar-target-generation-and-detection
status: done
language: MATLAB
---

# BoJi07/Radar-target-generation-and-detection

## Опис
MATLAB-проект з повним прикладом FMCW radar pipeline @ 77 GHz: target range/velocity → beat signal → 1D FFT (range) → 2D FFT (range-Doppler) → 2D CFAR.

## Структура
1. Radar specifications setup
2. 1D FFT для range
3. 2D FFT для range-velocity map
4. 2D-CFAR з вкладеними циклами по detection matrix
- **1024 range cells × 128 Doppler cells**

## CFAR variant
2D CA-CFAR через training + guard cells

## License
Не вказано в README

## Релевантність
- **Stage 1**: канонічний reference implementation для valid algorithm в MATLAB
- Можна **запустити локально** і порівняти output з нашим C++/CUDA blok (ground truth)
- Параметри (1024×128) — типові для нашого diff: 4096 FFT × N Doppler bins

## Посилання
- [[ext-github-cfar-28]] — Udacity SFND варіант
- [[ext-github-cfar-29]], [[ext-github-cfar-30]], [[ext-github-cfar-31]] — варіації SFND
- [[ext-cfar-theory-02]] — MATLAB 2D CFAR Detector API
