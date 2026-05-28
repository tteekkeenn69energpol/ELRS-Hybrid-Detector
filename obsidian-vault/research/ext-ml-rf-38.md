---
tags: [external, KB-extra, group-7, autoencoder, network, anomaly, tf-analysis, tangential]
created: 2026-05-28
type: paper
stage: 4
source_url: https://pmc.ncbi.nlm.nih.gov/articles/PMC11914985/
status: done
authors: Purohit R., Kumar S., Sayyad S., Kotecha K.
venue: MethodsX (Elsevier)
year: 2025
---

# Time-Frequency Analysis + Autoencoder для anomaly detection

## Цитування
Purohit R., Kumar S., Sayyad S., Kotecha K. *Time-frequency analysis and autoencoder approach for network traffic anomaly detection.* MethodsX, 2025.

## Короткий зміст
**Network traffic anomaly detection** через комбінацію CWT + DTFT + STFT + autoencoder. Анализ packet size/duration через time-frequency, features → autoencoder, anomaly = reconstruction error.

## Архітектура
- **3 TF transforms**: CWT + DTFT + STFT (multi-view features)
- **Unsupervised autoencoder**: encoder (latent space) + decoder (reconstruction)
- Anomalies → elevated reconstruction error

## Dataset
**CICIDS 2017** — ~547k data points, network traffic features (flow duration, protocol, behavior).

## Results
- **95% detection accuracy**
- 72 anomalies identified
- Robust + scalable для real-time cybersecurity

## Релевантність до проєкту
**Tangential** — це **network anomaly detection**, не RF. Але є цінні методологічні lessons:

1. **Multi-view TF features** (CWT + STFT + DTFT) — concept застосовний для нашого Stage 4 NN: feed multiple representations одного IQ для richer learning
2. **Unsupervised autoencoder** для anomaly detection — alternative до supervised classifier для **новельних протоколів** (e.g., нові варіанти ZeLRS/MiELRS, які наш supervised NN не бачив)
3. **Reconstruction error threshold** — простий decision criterion → можна додати до Decision Fusion ([[11-latency-decision-fusion]])

## Можливе застосування
- "Unknown protocol detector" як safety net Stage 4: якщо supervised classifier невпевнений, autoencoder reconstruction error визначає anomaly
- **Catastrophic forgetting** ([[18-research-questions]] 5.4) — autoencoder менше схильний (unsupervised)

## Посилання
- [[05-tz4-nelora]] — наш Stage 4
- [[11-latency-decision-fusion]] — Fusion з reconstruction error
- [[18-research-questions]] — 5.4 catastrophic forgetting
- [[ext-cfar-theory-05]] — Emergent Mind FAR overview згадує ML-based FAR control
