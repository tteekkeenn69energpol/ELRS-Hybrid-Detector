---
tags: [external, KB-extra, group-7, ml, lora, cnn, spectrum-sensing, hot-paper]
created: 2026-05-28
type: paper
stage: 2-4
source_url: https://pmc.ncbi.nlm.nih.gov/articles/PMC12074172/
status: done
authors: Mutescu P-M., Popa V., Lavric A.
venue: MDPI Sensors (Basel)
year: 2025
---

# LoRa Communications Spectrum Sensing Based on AI

## Цитування
Mutescu P-M., Popa V., Lavric A. *LoRa Communications Spectrum Sensing Based on Artificial Intelligence: IoT Sensing.* Sensors (Basel), 2025.

## Короткий зміст
**Hybrid spectrum sensing + AI** для детекції і класифікації **LoRa Spreading Factors (SF7-SF12)** у wideband signals безпосередньо з **I/Q samples** (без spectrogram пере-перетворення).

## ML архітектура
- **1D CNN, 26 шарів, 258,950 trainable params** (~260k — компактно!)
- Hierarchical blocks з progressively larger filters (4 → 64)
- Batch norm + ReLU + max pooling + global average pooling
- **Input: raw I/Q** (значна перевага — bez STFT overhead)

## Dataset
- **156,000 LoRa samples** через 6 SF
- Channel impairments: Rician multipath, Doppler, clock offset
- SNR range: **-20 dB до +30 dB**

## Results (★★★★★)
| Setting | Accuracy |
|---------|---------|
| Empirical dataset | **99.69%** |
| Real SDR testing | **99.97%** |
| Live LoRa transceiver | 96.2% Pd, 99.16% precision, 95.4% recall |

## Architecture features
- Modular: AI processing separated from channel analytics
- Adaptable до інших протоколів

## Релевантність до проєкту
- **GOLDEN reference для Stage 4 NN** ([[05-tz4-nelora]], [[13-stage4-nelora-verifier-onnx]])
- **258k params, ~1D CNN** — точно потрапляє у наші Edge AI обмеження ([[16-edge-ai-fhss-tracker]] — 1.1M params [[23-flak-czyba-distributed-sensor-grid]] як baseline)
- **Raw I/Q input** — на ~10× менше data ніж spectrogram → faster Stage 4
- **SF7-SF12 classification** — ELRS використовує SF6-SF12, точно та сама задача
- **-20 до +30 dB** — наша операційна планка (-12 dB target)
- 99% на синтетиці → 96% на real → **synthetic→real gap = 4%**, помітно менше ніж 15-30% попередження у [[05-tz4-nelora]]. Чудовий benchmark.

## Action items
1. Прочитати full paper для деталей architecture (kernel sizes, dilations)
2. Спробувати їх 1D CNN architecture як baseline для нашого Stage 4
3. Compare наш ELRS dataset з їх 156k LoRa samples

## Посилання
- [[05-tz4-nelora]] — наш Stage 4 ТЗ
- [[13-stage4-nelora-verifier-onnx]] — ONNX обгортка
- [[23-flak-czyba-distributed-sensor-grid]] — 1.1M params benchmark
- [[18-research-questions]] — питання 1.7 про I/Q vs spectrogram
