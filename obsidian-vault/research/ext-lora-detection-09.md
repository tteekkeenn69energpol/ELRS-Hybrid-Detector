---
tags: [external, KB-extra, group-2, lora, preamble, threshold-optimization]
created: 2026-05-28
type: paper
stage: 3
source_url: https://www.researchgate.net/publication/366523206_LoRa_Preamble_Detection_with_Optimized_Thresholds
status: partial
authors: Kang et al.
venue: IEEE (likely IoT Journal / Transactions)
year: 2023
doi_lookup: 10443232 (corrections), 9997090 (main)
---

# LoRa Preamble Detection With Optimized Thresholds

## Цитування
Kang et al. *LoRa Preamble Detection With Optimized Thresholds.* IEEE, 2023.
(IEEE Xplore ID 9997090; corrections at 10443232; ADS: 2023IITJ...10.6525K)

## Короткий зміст
Threshold-based LoRa preamble detection — стандарт для compatibility з LoRa. Існуючі методи **підбирають пороги евристично** → низька продуктивність. Стаття **оптимізує пороги**, максимізуючи Pd при constraint на FAR.

## Алгоритм
- Унікальна формалізація **coherent та non-coherent** preamble detection procedures
- Performance analysis обох
- **Joint optimization двох порогів (k, γ)**
- Найбільший gain у **низькому SNR** і при **малих FAR**

## Релевантність до проєкту
- **Stage 3** (Dechirp+MF, [[02-tz1-dechirp-mf]]): прямий вхід для нашого Preamble Validator (8 up-chirps + Sync Word)
- **Stage 1** (CFAR threshold): можливість аналогічно оптимізувати наш `cfar_threshold_db` під target FAR замість евристики "4.0"
- ELRS protocol: ELRS використовує 8 однакових up-chirps + Sync → формалізація з цієї статті прямо застосовна

## Посилання
- [[02-tz1-dechirp-mf]] — наш Preamble Validator
- [[ext-lora-detection-10]] — ELRS FAQ
- [[ext-cfar-theory-04]] — FAR теорія

## Примітка
ResearchGate 403. Інформація з WebSearch + IEEE Xplore індексу. Корекції доступні у IEEE 10443232.
