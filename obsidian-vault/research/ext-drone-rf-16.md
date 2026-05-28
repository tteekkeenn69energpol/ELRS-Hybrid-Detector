---
tags: [external, KB-extra, group-3, cfar, traffic, advi, skewness]
created: 2026-05-28
type: paper
stage: 1
source_url: https://www.mdpi.com/2079-9292/14/7/1474
status: done
authors: Tian Feng, Wei Tianyu, Fu Weibo, Wang Siyuan
venue: MDPI Electronics
year: 2025
volume: 14
issue: 7
doi: "10.3390/electronics14071474"
---

# ADVI-CFAR — Adaptive Discriminant Variation Index CFAR

## Цитування
Tian F., Wei T., Fu W., Wang S. *Research on Target Detection Algorithm for Complex Traffic Scenes Based on ADVI-CFAR.* Electronics, 2025, 14(7), 1474. DOI 10.3390/electronics14071474.

## Короткий зміст
Для traffic-radar з interfering targets + clutter reference cells пропонує **ADVI-CFAR**. Враховує:
1. **Background power transition point** для оцінки uniformity у reference window
2. **Higher-order skewness clutter** (а не Gaussian) для розрахунку background power threshold index

Підвищує точність background estimation у complex backgrounds.

## Ключові ідеї
- **Variation Index** як discriminant — оцінює зміну power у reference window
- **Skewness** як higher-order statistic — non-Gaussian assumption
- Адаптивний поріг залежно від discriminant

## Релевантність до проєкту
- **Stage 1**: ELRS ефір нагадує "traffic-радар" — багато некорельованих джерел interference (WiFi, BT, мікрохвильовки) **+ swarm drones**
- **Variation index** як local heterogeneity detector — дешева альтернатива на наш CFAR
- Skewness — хороший indicator що environment **не Rayleigh**

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[ext-drone-rf-13]] — теж non-homogeneous (power heterogeneous)
- [[ext-drone-rf-14]] — теж non-Gaussian (α-stable)
