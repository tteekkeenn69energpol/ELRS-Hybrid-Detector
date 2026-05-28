---
tags: [external, KB-extra, group-1, cfar, tutorial, adaptive-threshold]
created: 2026-05-28
type: tutorial
stage: 1
source_url: https://wirelesspi.com/adaptive-thresholding-in-radar-detection-using-constant-false-alarm-rate-cfar-techniques/
status: done
---

# Adaptive Thresholding in Radar Detection — CFAR (WirelessPi)

## Короткий зміст
Туторіал по адаптивному thresholding через CFAR: поріг змінюється на основі локального background interference. Розглянуто CA-CFAR, OS-CFAR, GO/SO-CFAR.

## Ключові ідеї / формули
- **CA-CFAR**: `T = α · P_n`, де `α` визначається бажаним Pfa, `P_n` — average power training cells. Швидко, для homogeneous noise.
- **OS-CFAR**: сортує training samples, вибирає k-у порядкову. Робастно проти strong interferers та closely-spaced targets.
- **Guard cells**: щоб target не "забруднював" noise estimate.
- **Training cells**: характеризують background.
- **GO/SO**: greatest/smallest з лівої/правої половин — для clutter edges.

## Tradeoff
- CA: simple + fast, але падає в non-homogeneous
- OS: robust, але обчислювально дорожчий (sort)
- Choice: залежить від оточення і обмежень

## Релевантність до проєкту
- **Stage 1**: освіжає чому ми йдемо в OS-CFAR vs CA — основне виправдання багатоцільового середовища ELRS
- Корисно для onboarding docs / навчальних матеріалів

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[21-os-cfar-realtime-impl]]
- [[ext-cfar-theory-02]] — MATLAB API
- [[ext-cfar-theory-04]] — FAR теорія
