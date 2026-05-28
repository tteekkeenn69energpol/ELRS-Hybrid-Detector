---
tags: [external, KB-extra, group-6, github, gnuradio, fhss, sandia, burst-detection]
created: 2026-05-28
type: github
stage: 1-2
source_url: https://github.com/sandialabs/gr-fhss_utils
status: done
language: C++/Python
provenance: Sandia National Laboratories
---

# sandialabs/gr-fhss_utils — GNU Radio FHSS utilities

## Опис
**Sandia National Labs** OOT-модуль GNU Radio для **frequency-hopping spread-spectrum** сигналів. Детекція + аналіз narrowband bursts в wideband captures зі збереженням time/freq metadata.

## Дві функціональні зони
1. **Burst detection + downconversion** — derived з gr-iridium project
2. **Dataset dehopper** — baseband all bursts у high-fidelity capture (для reverse engineering FHSS sequences)

## Алгоритм dehopper (two-stage)
1. **Coarse FFT** → identify peaks > amplitude threshold
2. **Fine-frequency correction** через instantaneous frequency averaging

Працює добре для **FSK сигналів**; інші модуляції потребують додаткової роботи.

## Структура
- Python hierarchical blocks (installed during build)
- GRC hier blocks в `examples/`
- **Без external OOT DSP залежностей** — приємно для production
- Related: `gr-pdu_utils` (Sandia ecosystem)

## Релевантність до проєкту
- **Stage 1+2 jackpot**: FHSS детекція — це **точно наш use-case** ELRS. ELRS = FHSS поверх LoRa CSS
- **Burst detection** блок — можливо повністю замінює наш Stage 1 baseline (тільки CSS-detection треба додати)
- **Dehopper** — пряма основа для нашого FHSS Tracker ([[16-edge-ai-fhss-tracker]])
- ELRS modulates LoRa CSS (не FSK) → coarse FFT + correction треба підлаштувати
- **Метадані bursts** (time, freq) — точно те що ми зберігаємо у hop_map.json (`missions/mission_01_cartographer/output/`)

## Action items
1. Clone і прочитати full source
2. Перевірити чи burst detector сумісний з C++ Stage 1 message API
3. Дослідити чи dehopper можна reuse як основу для FHSS Tracker

## Посилання
- [[16-edge-ai-fhss-tracker]] — наш FHSS Tracker (direct overlap)
- [[10-gnuradio-flowgraph]] — інтеграція OOT-модулів
- [[ext-lora-detection-10]] — ELRS FHSS protocol
- `missions/mission_01_cartographer/` — наш cartographer проект
