---
tags: [external, KB-extra, group-1, cfar, far, tutorial]
created: 2026-05-28
type: tutorial
stage: 1
source_url: https://www.radartutorial.eu/01.basics/False%20Alarm%20Rate.en.html
status: done
---

# False Alarm Rate (FAR) — Radartutorial.eu

## Короткий зміст
Базове пояснення FAR і Pfa: false alarm = noise/interference exceeding threshold. FAR = false targets per PRT ÷ range cells.

## Ключові формули / поняття
- **High threshold**: знижує false alarm, але зменшує detection probability
- **Low threshold**: підвищує sensitivity, але FA маскують реальні targets
- **CFAR**: адаптивно тримає Pfa constant незалежно від noise/clutter
- Припущення Rayleigh-distributed noise across range cells (для базових формул)

## Варіанти CFAR (згадані)
- CA-CFAR
- CAGO-CFAR
- OS-CFAR
- CASH-CFAR

## Релевантність до проєкту
- **Stage 1**: фундаментальне визначення Pfa = 10⁻⁴..10⁻⁶ як цільова метрика
- Корисно для обґрунтування `cfar_threshold_db = 4.0` у наших flowgraph variables ([[10-gnuradio-flowgraph]])
- Підтверджує що Rayleigh-припущення — стартова точка для ELRS noise floor estimation

## Посилання
- [[ext-cfar-theory-03]] — практичний tutorial
- [[ext-cfar-theory-05]] — модерні підходи до FAR
- [[08-stage1-oscfar-cpp]]
