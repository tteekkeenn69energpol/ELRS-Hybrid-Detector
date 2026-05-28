---
tags: [knowledge-builder, research, questions, deep-dive]
created: 2026-05-28
type: analysis
stage: all
status: open
drive_id: 1ZGTAB3JbWayciNdbduzoy_oinHVuSJFlRQVPVwSYY9o
source: 18_research_questions.md
---

# Дослідницькі питання (45 питань у 5 розділах)

## Призначення
Каталог відкритих питань, які потрібно дослідити DSP/ML командою. Використовується dsp-research агентом для пріоритизації досліджень.

## Структура
### Розділ 1: Архітектура та принципи (9 питань)
Фокус: CNN/ResNet/Transformer/CVNN/MoE; skip-connections при низькому SNR; CVNN для збереження фази; window size 128-1024; Early Exit + cascade; I/Q vs spectrogram vs A/P; kernel size для діагональних чирпів; CNN-LSTM/TCN гібриди.

### Розділ 2: Алгоритми та математика (9 питань)
Focal Loss, Center/Triplet Loss; SCM/SCF циклостаціонарність; phase unwrapping для A/P; SGDM vs Adam; self-attention для шумоподавлення; STFT параметри проти spectral leakage; cycle frequencies для ELRS preamble; Berlekamp-Massey для відновлення LFSR / FHSS prediction.

### Розділ 3: Реалізація та оптимізація (9 питань)
QAT vs PTQ для INT8 на Jetson/Coral; TensorRT для CVNN; CHWN vs NCHW; shared memory tiling, kernel fusion для 2D OS-CFAR; pruning (channel vs unstructured) сумісно з TPU/TensorRT; CUDA occupancy та register pressure; ZeroMQ / shared memory C++↔Python; Nsight Compute/Systems; обмеження Jetson Orin Nano + Coral TPU для >500k params.

### Розділ 4: Тестування та валідація (9 питань)
Pd / Pfa / F1 / ROC-AUC при глушінні; синтетичний датасет (CFO, phase noise, multipath); обсяг fine-tuning vs RadioML 2018.01A; augmentation на unseen SNR; p95 latency на Edge; A/B test cascade vs end-to-end; калібрування SDR (HackRF/ADRV9009); довготривала стабільність; confusion matrix + t-SNE для confidence 0.4-0.6.

### Розділ 5: Інтеграція та масштабування (9 питань)
Confidence gating з hysteresis; Active Learning для hard samples; Federated Learning без сирих даних; catastrophic forgetting при fine-tuning на ZeLRS/MiELRS; SigMF / VITA-49 формат; hot-reload конфігу; Grad-CAM / attention maps; масштабування Lab → Field; protocols (confidentiality, integrity, logging) для defense-grade.

## Як використовувати
- dsp-research та cpp-dev агенти ведуть експерименти за пріоритетними питаннями
- Відповіді логуються в `/obsidian/logs/research-answers-<date>.md`
- Питання з підтвердженими відповідями переносяться у `/obsidian/docs/`

## Залежності
- Інформує всі ТЗ
- Особливо важливо для [[05-tz4-nelora]], [[15-rf-fingerprinting-tz]], [[16-edge-ai-fhss-tracker]]
- Окремі CUDA-питання — [[17-gpu-stft-cfar-analysis]] / [[19-full-cuda-cpp-pipeline]]
