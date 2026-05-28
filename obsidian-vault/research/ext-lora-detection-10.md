---
tags: [external, KB-extra, group-2, elrs, expresslrs, faq, protocol]
created: 2026-05-28
type: docs
stage: all
source_url: https://www.expresslrs.org/faq/
status: done
---

# ExpressLRS FAQ — офіційна документація

## Короткий зміст
Офіційний FAQ ELRS-проекту. **Найавторитетніше джерело про сам протокол** для нашого детектора.

## Ключові факти про протокол

### Hardware та модуляція
- **Semtech SX12xx LoRa transceivers**
- Lightweight, highly optimized OTA protocol поверх LoRa CSS

### Frequency bands
- **900 MHz band** (915 MHz US ISM, наш цільовий)
- **2.4 GHz band**
- Cross-vendor compatibility у межах одного діапазону

### Packet rates
- **До 1000 Hz на 2.4 GHz** (serial RX + firmware + ≥921000 baud + disabled ADC filtering)
- Нижчі rates на 900 MHz
- Common rates: 25, 50, 100, 150, 200, 250, 500, 1000 Hz

### Channels
- До 16 channels
- 1-4: повна 10-bit resolution
- 5-16: scaled (Hybrid / Wide / mixed)

### FHSS (КРИТИЧНО для нашого детектора)
- **Binding phrase** seedає RNG, який визначає **frequency hopping pattern**
- Не secret, але унікальний per binding phrase → uniques hop sequence per pair
- Це робить FHSS Tracker завданням нетривіальним: треба або знати binding phrase, або реверсити LFSR

### Distinguishing factors
- Open source
- Lower cost vs commercial
- >100+ км range

## Релевантність до проєкту
- **ЦЕНТРАЛЬНЕ джерело** для всього проєкту
- **Stage 1**: підтверджує 915 MHz US ISM band (наш `center_freq = 915e6`)
- **Stage 2-3**: SX12xx → стандартні SF (7-12), BW (125/250/500 kHz)
- **Stage 4 + Fingerprint**: 25-1000 Hz packet rates → діапазон, який треба covering
- **FHSS Tracker** ([[16-edge-ai-fhss-tracker]]): seed → RNG → hop pattern; теоретично реверсуєме за достатньою кількістю спостережень
- **Cross-vendor**: добре для нашого RF fingerprinting — багато виробників

## Посилання
- [[02-tz1-dechirp-mf]] — Dechirping для CSS
- [[06-tz5-hybrid-pipeline]] — overall pipeline
- [[15-rf-fingerprinting-tz]] — Fingerprinting per vendor
- [[16-edge-ai-fhss-tracker]] — FHSS prediction
