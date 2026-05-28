---
tags: [external, KB-extra, group-1, cfar, far, overview, ml]
created: 2026-05-28
type: overview
stage: 1
source_url: https://www.emergentmind.com/topics/false-alarm-rate-far
status: done
---

# False Alarm Rate (FAR) — Emergent Mind overview

## Короткий зміст
Огляд FAR як концепту binary hypothesis testing: FAR = P(X > T | H0). Перекриває класичні методи і модерні ML-підходи.

## Ключові методи
- **CFAR techniques**: CA-CFAR, OS-CFAR, nonparametric rank-based
- **ML підходи**: invariant FAR через regularization (Maximum Mean Discrepancy penalties), CFARnet (deep learning з constraint на Pfa)

## Застосування
- Radar
- Anomaly / intrusion detection
- Astronomical photon-counting
- Compressive sensing

## Tradeoff
- Lower FAR ↑ threshold ↓ Pd
- Optimum залежить від cost-функції (missed vs analyst workload)

## Валідація
Емпірична калібрація на background-only observations критична — аналітичні формули можуть не співпадати з реальним розподілом.

## Релевантність до проєкту
- **Stage 1 → Stage 4**: підтверджує hybrid підхід — класичний CFAR + ML-based верифікатор з invariant FAR
- Згадка CFARnet — потенційний референс для [[05-tz4-nelora]]: NN з explicit Pfa constraint
- Methodology: ми маємо callibrate Pfa empirically на our noise floor (Aaronia + cable)

## Посилання
- [[ext-cfar-theory-04]] — basic FAR
- [[05-tz4-nelora]] — Stage 4 NN
- [[ext-ml-rf-37]] — CFARnet related works (якщо знайдемо у group 7)
