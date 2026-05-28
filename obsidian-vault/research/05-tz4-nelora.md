---
tags: [knowledge-builder, tz, analysis, stage4, neural, nelora, deep-learning]
created: 2026-05-28
type: analysis
stage: 4
status: approved-with-modifications
score: 8/10
drive_id: 1Ko2_-Vu2ZD-dEVUEkzpe4awtCQUuvRhkB1uquD_qdNs
source: 05_tz4_nelora_neural_detector.md
---

# ТЗ №4: NELoRa-style Neural-Enhanced Detector

## Вердикт
8/10 — APPROVED з модифікаціями. Підхід для екстремальних умов (SNR -16…-19 dB). **Використовувати як фінальний верифікатор тільки для "підозрілих" випадків**, не для кожного кандидата.

## Сильні сторони
- Deep Learning активно досліджується (RadioML, O'Shea et al.)
- Стійкість до низького SNR: -16…-19 dB, де класика падає
- Multi-task: детекція + параметри + confidence одночасно
- RF Fingerprinting через embeddings (ідентифікація конкретного передавача)
- Гнучкість входу: spectrogram / CWT / WVD

## Критичні проблеми
1. **Дані**: 100k+ синтетичних × кожна (SF,BW,SNR) комбінація, 10k+ реальних записів. Розмітка — складна.
2. **Synthetic→Real gap**: 95% на синтетиці → 60% на реальних. Потрібен Domain Adaptation, RF-aware augmentation, fine-tuning.
3. **Каскадна латентність**: сума Stage 1-4 ≈ 103 ms → не real-time. Потрібен confidence gating (Stage 4 тільки якщо 1-3 невпевнені).
4. **Архітектура**: EfficientNet-B3 (~12M params, ~1.8G FLOPs) → 8-15 ms на RTX 3070.

## Рекомендована стратегія
- Стиснений ViT/EfficientNet → ONNX → TensorRT INT8
- Trigger тільки при confidence з Stage 1-3 ∈ [0.4, 0.7]
- Active learning: логування hard samples для continuous fine-tuning

## Залежності
- Імплементація — [[13-stage4-nelora-verifier-onnx]]
- Координується через [[06-tz5-hybrid-pipeline]] і [[11-latency-decision-fusion]]
- RF Fingerprinting розширення — [[15-rf-fingerprinting-tz]]
- Edge AI deploy — [[16-edge-ai-fhss-tracker]]
