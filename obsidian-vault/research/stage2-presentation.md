---
tags: [stage-2, knowledge-builder, presentation, overview, architecture]
created: 2026-05-29
type: presentation
stage: 1
status: done
source: ELRS_Presentation_Slides.md
drive_id: 1NtWgaMMOHKmhsvfZSXG4vQ1W49Mz9fFe
---

# ELRS HYBRID DETECTOR — Презентація
**Multi-Stage Cascaded Detection & Jamming System**
Огляд проєкту, стан розробки та план реалізації
Травень 2026 | Конфіденційно

---

## Проблема (Слайд 1)

ELRS використовує LoRa CSS (Chirp Spread Spectrum) з FHSS.
Параметри невідомі: SF (7–12), BW (203k–1.6M Hz), hopping pattern.
MiELRS / ZeLRS — модифіковані версії зі зміненими паттернами.
SNR < -15 dB — класичні методи (energy detection) не працюють.

---

## 5-рівневий каскадний детектор (Слайд 2)

| Stage | Назва | Throughput |
|-------|-------|-----------|
| Stage 1 | 2D OS-CFAR Trigger | 100% потоку, ≤8ms |
| Stage 2 | Blind Estimation (DWT+CWT) | 1–5% потоку, ≤25ms |
| Stage 3 | Fine Detection (Dechirp+MF) | кандидати, ≤12ms |
| Stage 4 | Neural Verifier (CNN+ONNX) | <1% потоку, ≤15ms |
| Stage 5 | Decision Fusion | фінальне, ≤2ms |

**Ключовий принцип:** швидкі етапи фільтрують 95–99% даних.

---

## Системні KPI (Слайд 3)

| Метрика | Ціль |
|---------|------|
| End-to-end латентність | ≤ 50 мс |
| Pd @ -12 dB | ≥ 95% |
| Pd @ -17 dB | ≥ 80% |
| False Alarm Rate | ≤ 0.3% |

---

## Конкурентне позиціонування (Слайд 4)

| Параметр | Наш проєкт | R&S ARDRONIS | DroneShield |
|----------|------------|--------------|-------------|
| Ціна | $500–2k | $50k–200k+ | $15k–40k |
| Смуга | 200 MHz | 120 MHz | ~50 MHz |
| Латентність | ≤ 50 мс | ~100 мс | < 1 с |
| ELRS фокус | Оптимізовано | Загальний | Загальний |
| Модульність | Відкрита | Закрита | Закрита |

---

## Розширені модулі (Слайд 5)

- **RF Fingerprinting** (6 тижнів) — ідентифікація конкретного пристрою
- **FHSS Tracker** (6 тижнів) — передбачення наступного каналу за 0.5–2 мс
- **Edge AI Deploy** (6 тижнів) — Jetson/Coral/FPGA, ≤8Вт
- **Cognitive Jammer** (8 тижнів) — RL-агент PPO для адаптивної завади

---

## Стан на момент презентації (Слайд 6)

| Компонент | Код | Тести | Примітка |
|-----------|-----|-------|----------|
| Stage 1 (OS-CFAR) | ✅ 100% | ✅ PASS | **Закрито** Pfa=0, 86 MS/s |
| Stage 2 (Blind Est.) | 70% | 10% | GPU backend відсутній |
| Stage 3 (Dechirp+MF) | 75% | 15% | Найвища готовність |
| Stage 4 (Neural) | 40% | 0% | Немає моделі та датасету |
| GNU Radio OOT | 40% | 5% | Bindings не завершені |

*Примітка: Stage 1 закрито після презентації (коміт 308f60d)*

---

## Ризики (Слайд 8)

| Ризик | Ймов. | Стратегія |
|-------|-------|-----------|
| Python GIL при 100 MS/s | 90% | Stage 1 — тільки C++, lock-free queues |
| Відсутність реальних даних | 80% | Збір з першого тижня |
| Synthetic→Real gap (Neural) | 75% | Domain adaptation, active learning |
| Memory bandwidth GPU | 50% | Overlap 75%, batch processing |

---

## Посилання

- [[docs/pipeline-overview]] — архітектурний огляд каскаду
- [[stage2-tz-hybrid-pipeline]] — TZ#5 (детальний розпис)
- [[stage2-tz-dwt-cwt]] — Stage 2 spec
- [[00-overview/project-overview]] — поточний стан
- [[14-commercial-defence-analysis]] — детальне порівняння комерційних рішень
