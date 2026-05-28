---
tags: [external, KB-extra, group-3, cfar, radar, mdpi, adaptive-estimation]
created: 2026-05-28
type: paper
stage: 1
source_url: https://www.mdpi.com/2072-4292/16/13/2508
status: done
authors: Xiao Daipeng, Liu Weijian, Chen Hui, Li Hao, Li Binbin
venue: MDPI Remote Sensing
year: 2024
volume: 16
issue: 13
doi: "10.3390/rs16132508"
---

# Adaptive Radar Target Detection in Power Heterogeneous Clutter (Alternate Estimation)

## Цитування
Xiao D., Liu W., Chen H., Li H., Li B. *An Adaptive Radar Target Detection Method Based on Alternate Estimation in Power Heterogeneous Clutter.* Remote Sensing, 2024, 16(13), 2508. DOI 10.3390/rs16132508.

## Короткий зміст
Multichannel radar часто потребує training samples для covariance matrix clutter. При сильно нерівномірному terrain і складному EM environment training data має іншу статистику, ніж data-під-тестом. Розв'язує **power-heterogeneous clutter** — однакова covariance structure, але різні power scales.

## Алгоритм
- **Alternate estimation** одночасно для target і clutter power
- Тестування критеріями: **GLRT, Rao, Wald, Gradient, Durbin**
- Адаптивно оцінює power mismatch у різних cells

## Релевантність до проєкту
- **Stage 1**: ELRS spectrum **дуже power-heterogeneous** (WiFi бурсти, мікрохвильовки) — наш CFAR має це враховувати
- Концепція "однакова PDF, різний power" чудово підходить до 915 MHz ISM band
- GLRT/Rao detector як **друга стадія верифікації** після baseline CA/OS-CFAR

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[ext-cfar-theory-01]] — TF-CFAR (теж non-stationary)
- [[ext-cfar-theory-08]] — Wilcoxon non-parametric
- [[ext-drone-rf-14]] — теж CFAR в non-Gaussian
