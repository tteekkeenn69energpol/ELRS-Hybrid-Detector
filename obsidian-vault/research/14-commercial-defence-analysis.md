---
tags: [knowledge-builder, analysis, competitive, defense, benchmarking]
created: 2026-05-28
type: analysis
stage: all
status: done
drive_id: 13RqU9PfeDUYKw-uzwK2meNsoEe4o8LmZVNM3ipPyuh0
source: 14_commercial_defence_analysis.md
---

# Аналіз комерційних defence рішень

## Конкуренти
| Система | Smuga | Метод | FHSS | Латентність | Ціна |
|---------|-------|-------|------|------------|------|
| **Наш проект** | 700M-2.5G | Dechirp+ML+CFAR | ✅ LoRa CSS | ≤50 ms | $500-2k (DIY) |
| R&S ARDRONIS | 70M-6G | RF fingerprint+AI | ✅ | ~100 ms | $50k-200k |
| DroneShield RfPatrol Mk2 | 70M-6G | Signature db+ML | ✅ | <1 s | $15k-40k |
| Fortem TrueView R30 | 300M-6G | Radar+RF | ❌ | <100 ms | $100k-500k |
| SRC Silent Archer | 20M-6G | Multi-sensor fusion | ✅ adaptive | <50 ms | $200k-1M |

## Що роблять лідери правильно
- **R&S ARDRONIS**: RF fingerprinting (модель, не "є дрон"), FHSS-tracking, пасивна детекція
- **DroneShield**: wearable (800g, 8+ годин), 200+ сигнатур OTA, Direction Finding
- **SRC**: software-defined (оновлення без заміни заліза), multi-sensor (RF+Radar+EO/IR+Acoustic)
- **Fortem**: AESA radar + AI (детекція автономних дронів без RF), 3D tracking

## Пропозиції для проєкту
1. **RF Fingerprinting Module** — окремий ТЗ ([[15-rf-fingerprinting-tz]])
2. **Edge AI deployment** — мобільна версія ([[16-edge-ai-fhss-tracker]])
3. **FHSS Tracker** — проактивна завада, передбачення наступної частоти
4. **Multi-sensor fusion** (опційно): додати акустику + EO
5. **Direction Finding** через 2+ Aaronia рознесених на 2-5 м

## Висновок
Проєкт спрямований у нішу між DIY (Hackathon-grade) та комерційним defence-grade. Унікальні переваги: відкрита архітектура, фокус на ExpressLRS/MiELRS/ZeLRS (специфічна загроза для України), вартість на 1-2 порядки нижча.

## Залежності
- Генерує [[15-rf-fingerprinting-tz]]
- Генерує [[16-edge-ai-fhss-tracker]]
- Інформує стратегію [[06-tz5-hybrid-pipeline]]
