---
tags: [external, KB-extra, group-1, cfar, time-frequency]
created: 2026-05-28
type: paper
stage: 1
source_url: https://www.researchgate.net/publication/221021928_A_time_frequency_approach_to_CFAR_detection
status: partial
authors: Layeghy S., et al.
---

# A Time-Frequency Approach to CFAR Detection

## Короткий зміст
Non-parametric CFAR detection через time-frequency (TF) аналіз. Сигнал шукається на spectrogram, локалізується в часі, потім детекція через adaptive thresholding. Передбачає роботу за умов невідомих параметрів clutter/noise/Doppler — там де класичні CFAR падають.

## Ключові ідеї / алгоритми
- Spectrogram → TF-локалізація candidates → adaptive threshold
- Незалежність від статистичних припущень про clutter (не Rayleigh-only)
- Підхід non-parametric — обходить обмеження CA/OS-CFAR при unknown clutter
- IEEE conference paper (також на ResearchGate id 221021928)

## Релевантність до проєкту
- **Stage 1**: альтернативний CFAR для ELRS, де ефір сильно non-homogeneous (LoRa CSS + WiFi + Bluetooth)
- TF-based підхід природньо лягає на наш STFT pipeline (вже маємо spectrogram → можна додати TF-CFAR layer)
- Може зменшити FAR без втрати Pd у складних сценаріях

## Посилання
- [[08-stage1-oscfar-cpp]] — основний CFAR Stage 1
- [[17-gpu-stft-cfar-analysis]] — STFT pipeline куди можна вкласти TF-CFAR
- [[ext-cfar-theory-08]] — інший non-parametric підхід (Wilcoxon)

## Примітка
ResearchGate повертає 403 для WebFetch. Інформація отримана через WebSearch (title/abstract). Для повного тексту потрібен manual download.
