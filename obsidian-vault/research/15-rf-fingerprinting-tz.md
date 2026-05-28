---
tags: [knowledge-builder, tz, rf-fingerprinting, stage4-5, identification, mielrs, zelrs]
created: 2026-05-28
type: tz
stage: 4.5
status: approved
version: "1.0"
priority: high
drive_id: 141SwC386kP-friVxw9sG-Ouufao64lEL5EnSHQVCwuM
source: 15_rf_fingerprinting_tz.md
---

# ТЗ: RF Fingerprinting Module для MiELRS/ZeLRS

## Призначення
Ідентифікація **конкретного передавача** на основі унікальних апаратних характеристик RF-тракту, навіть при однаковому протоколі (ELRS/ZeLRS/MiELRS).

Відрізняється від протокольної детекції: відповідає не "який протокол", а "який конкретний пристрій".

## Цілі
| Ціль | Пріоритет |
|------|-----------|
| Ідентифікація виробника (Radiomaster, TBS, HappyModel) | 🔴 |
| Детекція модифікованих протоколів (MiELRS, ZeLRS) | 🔴 |
| Whitelist/Blacklist (дружні/ворожі) | 🔴 |
| Розвідка обладнання противника | 🟡 |
| Адаптація завад | 🟡 |

## Джерела унікальності HW
| Джерело | Стабільність | Унікальність |
|---------|--------------|--------------|
| I/Q imbalance | Висока | ⭐⭐⭐⭐ |
| LO leakage (CFO) | Висока | ⭐⭐⭐ |
| Phase noise (PLL/VCO) | Середня | ⭐⭐⭐⭐ |
| PA nonlinearity | Висока | ⭐⭐⭐⭐⭐ |
| DAC quantization | Висока | ⭐⭐⭐ |
| Filter response | Висока | ⭐⭐⭐⭐⭐ |
| Transient response | Дуже висока | ⭐⭐⭐⭐⭐ |
| Clock jitter | Середня | ⭐⭐⭐ |

## Архітектура
- Feature extractors (I/Q imbalance, AM-AM/AM-PM, transient envelope, CFO drift, phase noise spectrum)
- Embedding network (CNN/ViT) → 128-dim vector
- Cosine similarity vs database / k-NN
- Whitelist/blacklist + confidence

## Реалізація
- Python module: `python/elrs_detector/rf_fingerprint.py`
- YAML config: feature selection
- API для додавання нових extractors

## Залежності
- Розширення [[13-stage4-nelora-verifier-onnx]] (через embeddings)
- Випливає з [[14-commercial-defence-analysis]] (R&S ARDRONIS)
- Edge версія: [[16-edge-ai-fhss-tracker]]
