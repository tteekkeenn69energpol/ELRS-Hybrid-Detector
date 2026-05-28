---
tags: [presentation, external, pdf, lora, css, interference-cancellation, sigcomm]
created: 2026-05-28
type: presentation
stage: 3
status: reference
drive_id: 1jCHNtVyyqp7BnMBslpAsjn6n8F2o0Nzl
source: 3452296.3472931.pdf
authors: Shahid, Philipose, Chintalapudi, Banerjee, Krishnaswamy
venue: ACM SIGCOMM '21
year: 2021
pages: 13
---

# CIC: Concurrent Interference Cancellation для LoRa

## Цитування
Shahid M.O., Philipose M., Chintalapudi K., Banerjee S., Krishnaswamy B.
*Concurrent Interference Cancellation: Decoding Multi-Packet Collisions in LoRa.*
ACM SIGCOMM '21, August 23-28, 2021. https://doi.org/10.1145/3452296.3472931

## Релевантність для проєкту
Глибоке розкриття LoRa CSS dechirping та обробки колізій — пряма теорія для **Stage 3 Dechirp+MF** ([[02-tz1-dechirp-mf]]).

## Ключові ідеї
- **CSS demodulation**: dechirp (множення на down-chirp) → sinusoid → FFT peak
- **CIC (Concurrent Interference Cancellation)**:
  - Розбиває символ на sub-symbols
  - Демодулює кожен незалежно
  - Перетин спектрів між sub-symbols вирізує всі interferers
- Відрізняється від SIC: не ітеративне декодування з різними power levels
- **10× capacity vs COTS gateway, 4× vs SOTA research**
- Працює на низькому SNR (де baseline LoRa decoders падають)
- Demonstration на COTS LoRa devices

## Що взяти у наш pipeline
1. Метод вирізання interfering peaks через sub-symbol decomposition — потенційно для Stage 3 при наявності декількох ELRS передавачів одночасно
2. Аналіз робастності CSS dechirping при низькому SNR
3. Експериментальна валідація з COTS пристроями — методологія для нашого тестування

## Залежності
- Теоретична база для [[02-tz1-dechirp-mf]]
- Може інформувати [[05-tz4-nelora]] (neural може вчитися "CIC-стиль" cancellation)
