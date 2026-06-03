---
tags: [knowledge-builder, index, sources]
created: 2026-05-28
status: done
type: index
---

# Sources Index — KB-2

19 Google Docs + 6 PDF статей + 40 зовнішніх посилань розпарсено (травень 2026).
Оригінальні експорти: Google Docs → `/tmp/kb2_downloads/`, PDFs → `/tmp/kb_pdfs/`, lincks → `/tmp/kb_links/`, копії PDFs у vault → `data/raw/pdf/`.

## Папка 1: Roles & Pipeline (17 документів)

| # | Note | Title | Type | Stage | Drive ID |
|---|------|-------|------|-------|----------|
| 01 | [[01-system-architect]] | РОЛЬ: System Architect & PM | role | all | `1GFe6POfDMYnWXDZnARCb9jhdCKabISs1nF7K6ZUbHFo` |
| 02 | [[02-tz1-dechirp-mf]] | ТЗ №1 — Dechirping + Matched Filter | tz | 3 | `1ap-IlA9ktxxskAv1T8IX44ETOnltv2DTAugnr00UcaQ` |
| 03 | [[03-tz2-dwt-cwt]] | ТЗ №2 — DWT+CWT Blind Estimator | analysis | 2 | `1Vbs1zRNZwq4G2huO4NoKEcJRsWSfzNrZgs9567Uw998` |
| 04 | [[04-tz3-wigner-hough]] | ТЗ №3 — Wigner-Hough Transform | analysis | 3-offline | `1olHyhAxaPrlSxIj-iR7LiDm9zeFqoZ-E0pamq1NOOTU` |
| 05 | [[05-tz4-nelora]] | ТЗ №4 — NELoRa Neural Detector | analysis | 4 | `1Ko2_-Vu2ZD-dEVUEkzpe4awtCQUuvRhkB1uquD_qdNs` |
| 06 | [[06-tz5-hybrid-pipeline]] | ТЗ №5 — Hybrid Multi-Stage Pipeline | tz | all | `1RVcTdm1QUuTNzKZN8TAZvG6wlRP0qhz7paVIcH7PBF4` |
| 07 | [[07-oot-gnuradio-skeleton]] | Скелет OOT GNU Radio модуля | code | all | `15IMY-c7cii9zdOAIUduyaUOFy9Mt9i2SRONT4Nb4jNM` |
| 08 | [[08-stage1-oscfar-cpp]] | Stage 1: OS-CFAR CMake + C++ | code | 1 | `1tVdVov4TD7-Gc8m1Q_MP9U7BKeexgneWeR146E54bN8` |
| 09 | [[09-stage2-blind-estimator-py]] | Stage 2: blind_estimator.py | code | 2 | `1m99f1Ip6XcGcW9gveQ0g4_2csKA39p92L8q4miUBzB4` |
| 10 | [[10-gnuradio-flowgraph]] | elrs_full_pipeline.grc | code | all | `190G2SDpFThmVm1iVdn4eejLND5ZNims29GkkboDXO1Q` |
| 11 | [[11-latency-decision-fusion]] | Latency Optimization + Decision Fusion | code | all | `17-FabGLcOmjwcgQdsqT1HuNah1gQXHUv6hEae02W12E` |
| 12 | [[12-adrv9009-artix7-migration]] | ADRV9009 + Artix-7 міграція | tz | 1-hw | `1s6bP-NMZByLtlLl08JObciV-noa4aTlVfaYOe8Is4-U` |
| 13 | [[13-stage4-nelora-verifier-onnx]] | Stage 4: NELoRa Verifier (ONNX) | code | 4 | `1SMbJRHAZALXmoRCKeMJ_6RbeMl7XUt_ZkKgY5dbCFQ8` |
| 14 | [[14-commercial-defence-analysis]] | Аналіз комерційних defence рішень | analysis | all | `13RqU9PfeDUYKw-uzwK2meNsoEe4o8LmZVNM3ipPyuh0` |
| 15 | [[15-rf-fingerprinting-tz]] | RF Fingerprinting Module ТЗ | tz | 4.5 | `141SwC386kP-friVxw9sG-Ouufao64lEL5EnSHQVCwuM` |
| 16 | [[16-edge-ai-fhss-tracker]] | Edge AI + FHSS Tracker ТЗ | tz | 4-edge | `1UA9q7uiAkaFfMMbYVucseOjUS8kWYI1pwW2sQR1Kp9o` |
| 17 | [[17-gpu-stft-cfar-analysis]] | GPU STFT+CFAR аналіз (9.5/10) | analysis | 1 | `1ZnVM6lGf4imF33KY_D6UEdOUyf15eSZC4yu1HEr_KPk` |

## Папка 2: CFAR датасети (2 документи)

| # | Note | Title | Type | Stage | Drive ID |
|---|------|-------|------|-------|----------|
| 18 | [[18-research-questions]] | ДОП_ПИТАННЯ (45 дослідницьких) | analysis | all | `1ZGTAB3JbWayciNdbduzoy_oinHVuSJFlRQVPVwSYY9o` |
| 19 | [[19-full-cuda-cpp-pipeline]] | Повний CUDA C++ Pipeline | code | 1 | `1u1MBG4g9JpRFzl-meG0LM57DqYwc2klbJ8jd6J2Cqrc` |

## Папка 3: Detector статті (PDF, KB-extra)

Зовнішні academic PDFs про CFAR, LoRa CSS, drone detection, GPU DSP. Текст витягнуто через PyMuPDF.

| # | Note | Title | Venue | Year |
|---|------|-------|-------|------|
| 20 | [[20-cic-lora-collision-decoding]] | Concurrent Interference Cancellation in LoRa | ACM SIGCOMM | 2021 |
| 21 | [[21-os-cfar-realtime-impl]] | Real-Time Implementations of OS-CFAR | Georgia Tech / AFRL | — |
| 22 | [[22-flak-drone-sensor-24ghz-sdr-fpga]] | Drone detection sensor 2.4 GHz ISM (SDR+FPGA) | IEEE Access | 2021 |
| 23 | [[23-flak-czyba-distributed-sensor-grid]] | RF Drone Detection — Distributed Sensor Grid | IEEE Access | 2023 |
| 24 | [[24-sorecau-wideband-usrp-rfnoc]] | Wideband Drone Monitoring (USRP + RFNoC) | MDPI Drones | 2026 |
| 25 | [[25-venter-sdr-pulse-doppler-gpu]] | SDR Pulse-Doppler Radar on GPUs (166p MEng) | U. of Pretoria | 2014 |

Drive folder: `1mHJIvGcn4yahW2v0xCIWco1_avR35wLo`

### Додаткові внутрішні матеріали (DSP Research / client)

| # | Note | Title | Role |
|---|------|-------|------|
| — | [[dataset-cfar]] | DATASET_CFAR (lowercase) — консолідована база знань OS-CFAR для ELRS | reference, R-1 input |
| — | [[DATASET_CFAR]] | DATASET_CFAR (uppercase) — Розділ 1: Архітектура та Принципи | reference (alt copy) |
| — | [[cfar email]] | ТЗ замовника — рекомендовані параметри (12.5 dB, k≈0.75·N, min_snr 7 dB) | client TZ, R-1 input |
| — | [[20-grcon25-elrs-gnuradio-paper]] | GRCon25 — ELRS Under Interference Using GNU Radio | paper |
| — | [[27-github-repos-reference]] | GitHub репозиторії — зовнішні референси (GR/LoRa/ELRS) | reference |

> Файли `dataset-cfar.md` та `DATASET_CFAR.md` — case-only duplicates, обидва
> збережено як приймали. `cfar email.md` — оригінал клієнтського ТЗ, є основним
> джерелом параметрів у [[../docs/cfar-spec|cfar-spec]] §34-47.

## External References (KB-extra, 2026-05-28) — 40 зовнішніх посилань

40 посилань з 8 тематичних груп. Префікс `ext-`. Завантажено через WebFetch / wget / curl(crossref) / WebSearch fallback. Дата обробки: **2026-05-28**. Власник: Knowledge Builder (re-activated). Process entry — [[../logs/decisions-log#kb-extra-2026-05-28|decisions-log § KB-extra]].

Розподіл за категоріями (всі 40 файлів проіндексовано нижче):
cfar-theory(8) · lora-detection(3) · drone-rf(6) · cuda-gpu(8) ·
github-cfar(6) · github-gnuradio(3) · ml-rf(4) · fmcw(2). **Дублікатів виявлено: 3**
(stubs з redirect — без імен у summary, деталі у таблицях нижче та у
`decisions-log § KB-extra`).

### Група 1 — CFAR теорія та алгоритми (8)

| # | Note | Title | Status |
|---|------|-------|--------|
| 1 | [[ext-cfar-theory-01]] | Time-Frequency Approach to CFAR Detection | partial (RG 403) |
| 2 | [[ext-cfar-theory-02]] | MATLAB 2-D CFAR Detector docs | done |
| 3 | [[ext-cfar-theory-03]] | Adaptive Thresholding CFAR tutorial (WirelessPi) | done |
| 4 | [[ext-cfar-theory-04]] | FAR overview (Radartutorial.eu) | done |
| 5 | [[ext-cfar-theory-05]] | FAR topic (Emergent Mind) | done |
| 6 | [[ext-cfar-theory-06]] | MSS-CFAR (Kamal 2023, sort-free) | done |
| 7 | [[ext-cfar-theory-07]] | ETJ Iraq article_82064 | UNAVAILABLE |
| 8 | [[ext-cfar-theory-08]] | Wilcoxon non-parametric CFAR (SAR) | done |

### Група 2 — LoRa / ELRS детекція (3)

| # | Note | Title | Status |
|---|------|-------|--------|
| 9 | [[ext-lora-detection-09]] | LoRa Preamble Detection w/ Optimized Thresholds | partial (RG 403) |
| 10 | [[ext-lora-detection-10]] | ExpressLRS FAQ — official | done |
| 11 | [[ext-lora-detection-11]] | CERN 2013: Two Apps Using CUDA (sliding window) | done |

### Група 3 — Drone / RF detection (6)

| # | Note | Title | Status |
|---|------|-------|--------|
| 12 | [[ext-drone-rf-12]] | Flak & Czyba 2023 — DUPLICATE of [[23-flak-czyba-distributed-sensor-grid]] | done |
| 13 | [[ext-drone-rf-13]] | Adaptive Radar Detection in Power Heterogeneous Clutter | done |
| 14 | [[ext-drone-rf-14]] | CFAR in PαS Sea Clutter (Fox's H-function) | done |
| 15 | [[ext-drone-rf-15]] | Joint Ship Detection TF + CFAR (HF radar) | done |
| 16 | [[ext-drone-rf-16]] | ADVI-CFAR for traffic radar | done |
| 17 | [[ext-drone-rf-17]] | Sorecau 2026 — DUPLICATE of [[24-sorecau-wideband-usrp-rfnoc]] | done |

### Група 4 — GPU CUDA оптимізація (8)

| # | Note | Title | Status |
|---|------|-------|--------|
| 18 | [[ext-cuda-gpu-18]] | NVIDIA Nsight Compute — Profiling Guide | done |
| 19 | [[ext-cuda-gpu-19]] | NVIDIA Nsight Compute — product page | done |
| 20 | [[ext-cuda-gpu-20]] | NERSC NVIDIA profiling tools workflow | done |
| 21 | [[ext-cuda-gpu-21]] | Profiling CUDA Applications (Dillhoff notes) | done |
| 22 | [[ext-cuda-gpu-22]] | NVIDIA: Using Shared Memory in CUDA C/C++ | done |
| 23 | [[ext-cuda-gpu-23]] | SO: Generalized sliding-window on GPU | partial (SO blocked) |
| 24 | [[ext-cuda-gpu-24]] | Numba CUDA kernels docs | done |
| 25 | [[ext-cuda-gpu-25]] | NVIDIA PVA RadarCFAR API (Jetson Orin) | done |

### Група 5 — GitHub CFAR repos (6)

| # | Note | Title | Status |
|---|------|-------|--------|
| 26 | [[ext-github-cfar-26]] | BoJi07/Radar-target-generation-and-detection (MATLAB) | done |
| 27 | [[ext-github-cfar-27]] | KAdamek/GPU_Overlap-and-save_convolution (CUDA) | done |
| 28 | [[ext-github-cfar-28]] | Swaroopainapurapu/Radar_2D_CFAR (CA+OS hybrid) | done |
| 29 | [[ext-github-cfar-29]] | nbarendes/SFND_Radar_2D_CIFAR_Process | done |
| 30 | [[ext-github-cfar-30]] | stevenliu216/SFND_Radar_Target_Generation_and_Detection | done |
| 31 | [[ext-github-cfar-31]] | sunsided/SFND_Radar_2D_CFAR | done |

### Група 6 — GitHub GNU Radio / SDR (3)

| # | Note | Title | Status |
|---|------|-------|--------|
| 32 | [[ext-github-gnuradio-32]] | gnuradio/gr-cuda — CUDA Support for GR 3.10+ | done |
| 33 | [[ext-github-gnuradio-33]] | sandialabs/gr-fhss_utils — FHSS utilities | done |
| 34 | [[ext-github-gnuradio-34]] | juhasch CFAR gist (PyTorch + Rust) | done |

### Група 7 — ML / AI для RF (4)

| # | Note | Title | Status |
|---|------|-------|--------|
| 35 | [[ext-ml-rf-35]] | DeepWave AI (AIR-T + AirStack) | done |
| 36 | [[ext-ml-rf-36]] | Mutescu 2025 — LoRa SF7-12 via 1D CNN (99.97%) | done |
| 37 | [[ext-ml-rf-37]] | Abratkiewicz 2022 — STFT + 2D CFAR + DBSCAN | done |
| 38 | [[ext-ml-rf-38]] | Purohit 2025 — TF + autoencoder anomaly detection | done |

### Група 8 — FMCW Radar / DSP (2)

| # | Note | Title | Status |
|---|------|-------|--------|
| 39 | [[ext-fmcw-39]] | R-RSP for FMCW (IEEE 10891638) | partial (no authors) |
| 40 | [[ext-fmcw-40]] | Venter 2014 — DUPLICATE of [[25-venter-sdr-pulse-doppler-gpu]] | done |

### KB-extra statistics
- **Total**: 40 links
- **done**: 33
- **partial** (рrobably accessible but blocked by paywall/anti-bot): 4 (#1, #9, #23, #39)
- **unavailable**: 1 (#7 — ETJ Iraq 404)
- **duplicates** виявлені й нотатки-стаби з redirect: 3 (#12, #17, #40)
- PDFs додано у `data/raw/pdf/`: 2 (`06_novel_target_detection_worst_radar.pdf`, `11_cern_2013_cuda.pdf`)

---

## Stage 2 Knowledge Base (KB-S2-1..KB-S2-4, 2026-05-29)

15 нових файлів для Stage 2 (Blind Parameter Estimator). Завантажено 2026-05-29.

### KB-S2-1 — Google Drive матеріали (2 папки, 4 файли)

**Папка 1** (`1AjaKtXUvsCoKfdeBpYp8gUn3iTs5JpCc` — "Blind Parameter Estimation (DWT + CWT)"):

| # | Note | Title | Drive ID |
|---|------|-------|----------|
| — | [[stage2-dwt-cwt-questions]] | 45 глибоких питань для DWT/CWT аналізу | `1KOylifrVXvcK9e1vWTlcPolVRUc2h7QHlYjB0-sIqNE` |
| — | [[stage2-arch-principles]] | Section 1: Architecture & Principles (NotebookLM) | `1NExLnRvTtnkV6euXQTdXwPtZiJGtJAIbkcCHFRNH0wo` |

**Папка 2** (`1YKR02MsWSyqnjr2D3bTtOO6IYHScgAsj` — "Dechirping + Matched Filter"):

| # | Note | Title | Drive ID |
|---|------|-------|----------|
| — | [[stage2-dechirp-math]] | Документ без назви — математика dechirp та ортогональність | `1Ych1K251gjWpdZQQox8CF7ceKEPBwrS1jiLWFTLkxgc` |
| — | [[stage2-dechirp-queries]] | LoRa CSS dechirping — дослідницькі запити | `16y0b2Cn6jrm4CPOaMeFao-GQ9DwdORwYzvDcIZDcqIs` |

### KB-S2-2 — Локальні TZ файли (stage2-* копії з frontmatter)

| # | Note | Source File | Stage |
|---|------|-------------|-------|
| — | [[stage2-tz-dwt-cwt]] | TZ_02_DWT_CWT_Blind_Parameter_Estimator.md | 2 |
| — | [[stage2-tz-dechirp-mf]] | TZ_01_Dechirping_Matched_Filter_Bank.md | 3 |
| — | [[stage2-tz-wigner-hough]] | TZ_03_Wigner_Hough_Transform.md | 2 (offline verifier) |
| — | [[stage2-tz-hybrid-pipeline]] | TZ_05_Hybrid_MultiStage_Pipeline.md | all |
| — | [[stage2-tz-gnuradio]] | TZ_06_GNU_Radio_Integration.md | all |
| — | [[stage2-oot-setup]] | OOT_Module_Setup_Instructions.md | all |
| — | [[stage2-flowgraph]] | Flowgraph_elrs_full_detector.md | all |
| — | [[stage2-presentation]] | ELRS_Presentation_Slides.md | all |

### KB-S2-3 — Synthesis нотатки (3 нові)

| # | Note | Зміст |
|---|------|-------|
| — | [[stage2-key-dwt]] | DWT для SF: sym5/db4/biorthogonal, Level 3–4, autocorr Detail, пік на 2^SF |
| — | [[stage2-key-cwt]] | CWT/SST для BW: Morlet, 4 target scales, SSST для ELRS, calibration table |
| — | [[stage2-key-confidence-gate]] | Combined score formula, пороги 0.4/0.7, false-trigger control, holdoff |

### KB-S2 Statistics
- **Total new files (KB-S2)**: 15
- **GDrive**: 4 (2 папки, 4 docx → txt → md)
- **Local TZ copies**: 8
- **Synthesis notes**: 3
- **Total vault files**: ~86

---

## Класифікація за типом

- **Role** (1): [[01-system-architect]]
- **ТЗ** (6): [[02-tz1-dechirp-mf]], [[06-tz5-hybrid-pipeline]], [[12-adrv9009-artix7-migration]], [[15-rf-fingerprinting-tz]], [[16-edge-ai-fhss-tracker]]
- **Analysis** (6): [[03-tz2-dwt-cwt]], [[04-tz3-wigner-hough]], [[05-tz4-nelora]], [[14-commercial-defence-analysis]], [[17-gpu-stft-cfar-analysis]], [[18-research-questions]]
- **Code** (6): [[07-oot-gnuradio-skeleton]], [[08-stage1-oscfar-cpp]], [[09-stage2-blind-estimator-py]], [[10-gnuradio-flowgraph]], [[11-latency-decision-fusion]], [[13-stage4-nelora-verifier-onnx]], [[19-full-cuda-cpp-pipeline]]
- **Presentation/PDF** (6): [[20-cic-lora-collision-decoding]], [[21-os-cfar-realtime-impl]], [[22-flak-drone-sensor-24ghz-sdr-fpga]], [[23-flak-czyba-distributed-sensor-grid]], [[24-sorecau-wideband-usrp-rfnoc]], [[25-venter-sdr-pulse-doppler-gpu]]

## Класифікація за каскадом

- **Stage 1 (OS-CFAR Trigger)**: [[08-stage1-oscfar-cpp]], [[17-gpu-stft-cfar-analysis]], [[19-full-cuda-cpp-pipeline]], [[12-adrv9009-artix7-migration]] (HW), [[21-os-cfar-realtime-impl]] (ext), [[22-flak-drone-sensor-24ghz-sdr-fpga]] (ext), [[24-sorecau-wideband-usrp-rfnoc]] (ext), [[25-venter-sdr-pulse-doppler-gpu]] (ext)
- **Stage 2 (Blind Estimator)**: [[03-tz2-dwt-cwt]], [[09-stage2-blind-estimator-py]], [[stage2-tz-dwt-cwt]], [[stage2-arch-principles]], [[stage2-dwt-cwt-questions]], [[stage2-key-dwt]], [[stage2-key-cwt]], [[stage2-key-confidence-gate]]
- **Stage 3 (Dechirp+MF)**: [[02-tz1-dechirp-mf]], [[stage2-tz-dechirp-mf]], [[stage2-dechirp-math]], [[stage2-dechirp-queries]], [[04-tz3-wigner-hough]] (offline), [[20-cic-lora-collision-decoding]] (ext)
- **Stage 4 (Neural Verifier)**: [[05-tz4-nelora]], [[13-stage4-nelora-verifier-onnx]], [[23-flak-czyba-distributed-sensor-grid]] (ext)
- **Stage 4.5 (Fingerprinting)**: [[15-rf-fingerprinting-tz]]
- **Edge / FHSS**: [[16-edge-ai-fhss-tracker]]
- **Координація / інтеграція**: [[01-system-architect]], [[06-tz5-hybrid-pipeline]], [[07-oot-gnuradio-skeleton]], [[10-gnuradio-flowgraph]], [[11-latency-decision-fusion]]
- **Strategy / R&D**: [[14-commercial-defence-analysis]], [[18-research-questions]]
