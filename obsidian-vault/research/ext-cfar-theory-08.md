---
tags: [external, KB-extra, group-1, cfar, wilcoxon, non-parametric, sar]
created: 2026-05-28
type: paper
stage: 1
source_url: https://www.themoonlight.io/en/review/wilcoxon-nonparametric-cfar-scheme-for-ship-detection-in-sar-image
status: done
---

# Wilcoxon Nonparametric CFAR Scheme (огляд)

## Короткий зміст
Огляд статті про **Wilcoxon non-parametric CFAR** для детекції суден у SAR-зображеннях. Метод **distribution-free** — стабільний при змінному clutter (rough sea), де параметричні CFAR падають.

## Ключова ідея
- **Rank-based sliding window**: test cells + reference cells → **rank-sum statistic**
- Не припускає конкретного розподілу (Rayleigh, K, Weibull) — працює "на ранжируванні"
- Тримає constant FAR незалежно від форми clutter PDF

## Результати (з огляду)
- Тестовано на Radarsat-2, ICEYE-X6, Gaofen-3 датасетах
- FAR ≈ 10⁻⁴ robust
- Superior weak ship detection in rough seas
- Швидко (rank-statistic простіше за sort)

## Переваги vs параметричні CFAR
- Не потребує підгону розподілу
- Стабільний у non-stationary clutter

## Релевантність до проєкту
- **Stage 1**: альтернатива OS-CFAR для **time-varying ELRS spectrum** (з'являється/зникає WiFi, мікрохвилівки)
- Rank-sum проще ніж full sort → потенційно швидше на FPGA
- Поєднується з [[ext-cfar-theory-01]] (TF-CFAR) — обидва non-parametric

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[ext-cfar-theory-01]] — TF-CFAR (також non-parametric)
- [[ext-cfar-theory-06]] — MSS-CFAR (теж sort-free)
