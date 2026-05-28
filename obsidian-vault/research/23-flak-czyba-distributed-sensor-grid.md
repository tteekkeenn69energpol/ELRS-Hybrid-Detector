---
tags: [presentation, external, pdf, drone-detection, sensor-grid, cnn, preamble, sdr-fpga]
created: 2026-05-28
type: presentation
stage: 1-2-4
status: reference
drive_id: 1-8pHfga5276z14jt-kMIBiBiJZmSkxyb
source: RF_Drone_Detection_System_Based_on_a_Distributed_S.pdf
authors: Flak, Czyba
venue: IEEE Access
year: 2023
pages: 15
doi: "10.1109/ACCESS.2023.3340133"
---

# RF Drone Detection System на розподіленій сенсорній сітці (HW-accelerated + CNN)

## Цитування
Flak P., Czyba R. *RF Drone Detection System Based on a Distributed Sensor Grid With Remote Hardware-Accelerated Signal Processing.* IEEE Access, 2023. DOI 10.1109/ACCESS.2023.3340133.
Silesian University of Technology, Gliwice, Poland.

## Релевантність для проєкту
**Найближчий аналог нашій архітектурі**: HW-accelerated energy detection + ML на preamble pattern + distributed sensors. Підтверджує життєздатність всього нашого підходу.

## Ключові цифри
- **-8.7 dB SNR margin** для analytical energy detector stage (наш стартовий рівень CFAR)
- **CNN: 1.1M параметрів**, 99.93% simulation accuracy при **-9.5 dB SNR**
- Quantization для embedded platform — без значної втрати точності
- Standalone або distributed sensor grid (Ethernet)

## Архітектура
1. **HW-accelerated energy sensing** → витягування data frames з noise
2. **Spectrogram-based representation** з оптимізацією компонування
3. **ML на preamble pattern recognition** → ідентифікація drone (мала кількість обчислень, бо preamble коротший за весь frame)
4. Дистрибутивна архітектура поверх стандартного Ethernet
5. Embedded deployment з квантизацією

## Що взяти у наш pipeline
1. **Pattern**: HW Stage 1 (energy/CFAR) + ML Stage 4 (тільки на коротких preamble фрагментах) → той самий підхід, що в [[06-tz5-hybrid-pipeline]]
2. **1.1M params benchmark** — реалістична верхня межа для нашого NN, що влізає в Edge
3. **-9.5 dB target** — реалістична планка, ми ставимо собі -12 dB
4. **Distributed sensor grid** через Ethernet — практичний рецепт для [[14-commercial-defence-analysis]] пропозиції "multi-sensor fusion" і Direction Finding

## Залежності
- Розширює [[22-flak-drone-sensor-24ghz-sdr-fpga]]
- Підтверджує метрики [[05-tz4-nelora]] (NN при низькому SNR)
- Архітектурний паттерн [[06-tz5-hybrid-pipeline]]
- Edge варіант [[16-edge-ai-fhss-tracker]]
- Multi-sensor → [[14-commercial-defence-analysis]]
