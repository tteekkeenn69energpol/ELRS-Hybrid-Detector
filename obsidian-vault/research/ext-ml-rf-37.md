---
tags: [external, KB-extra, group-7, stft, cfar, dbscan, retrieval, hot-paper]
created: 2026-05-28
type: paper
stage: 1-2
source_url: https://pmc.ncbi.nlm.nih.gov/articles/PMC9413984/
status: done
authors: Karol Abratkiewicz
venue: MDPI Sensors (Basel)
year: 2022
---

# Radar Detection-Inspired Signal Retrieval from STFT

## Цитування
Abratkiewicz K. *Radar Detection-Inspired Signal Retrieval from the Short-Time Fourier Transform.* Sensors (Basel), 2022.

## Короткий зміст
**Adaptive multicomponent signal decomposition** через STFT. Підхід **inspired by CFAR**:
1. Detect high-magnitude regions у TF (CFAR-like)
2. **DBSCAN cluster** detected points
3. Build time-frequency masks
4. Extract components без noise/interference
5. **Inverse STFT** для reconstruction

## Алгоритм
- **2D CFAR** for adaptive thresholding на spectrogram
- **DBSCAN clustering** для grouping detected points (per-component grouping)
- Spectrogram zero-based mask refinement
- ISTFT для signal reconstruction

## Dataset
- Simulated nonlinear chirps
- **Real ATC radar pulses** з Warsaw Chopin Airport

## Results
- **10-15 dB improvement** reconstruction quality vs vertical synchrosqueezing та triangulation-based методів
- Особливо добре на vertical components + transients

## Релевантність до проєкту
- **DIRECT PIPELINE MATCH**: STFT → 2D CFAR → cluster — це **точно наш Stage 1 + Stage 2 pipeline**!
- **DBSCAN clustering після CFAR** — те що ми робимо у `peak_detect_kernel.cu` NMS, але DBSCAN дає richer info (component grouping)
- **TF masking + ISTFT** — потужний підхід для **isolation окремих ELRS hop sequences** з многоаудійного ефіру
- 10-15 dB quality improvement — значне покращення SNR після retrieval, що допоможе Stage 3 dechirping
- Real-data validation (ATC radar) — додаткова validation для подібних RF задач

## Action items
1. Прочитати алгоритм клейстеру DBSCAN params
2. Тестувати DBSCAN-after-CFAR як post-processing у нашому Stage 1
3. Спробувати ISTFT-based hop isolation для FHSS tracker ([[16-edge-ai-fhss-tracker]])

## Посилання
- [[08-stage1-oscfar-cpp]] — наш Stage 1
- [[19-full-cuda-cpp-pipeline]] — peak_detect_kernel.cu
- [[ext-drone-rf-15]] — теж TF + CFAR (HF radar ships)
- [[ext-cfar-theory-01]] — TF approach to CFAR
- [[16-edge-ai-fhss-tracker]] — FHSS hop isolation
