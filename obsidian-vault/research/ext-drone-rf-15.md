---
tags: [external, KB-extra, group-3, cfar, time-frequency, hf-radar, ship-detection]
created: 2026-05-28
type: paper
stage: 1-2
source_url: https://www.mdpi.com/2072-4292/13/8/1548
status: done
authors: Yang Zhiqing, Tang Jianjiang, Zhou Hao, Xu Xinjun, Tian Yingwei
venue: MDPI Remote Sensing
year: 2021
volume: 13
issue: 8
doi: "10.3390/rs13081548"
---

# Joint Ship Detection — TF Domain + CFAR з HF Radar

## Цитування
Yang Z., Tang J., Zhou H., Xu X., Tian Y. *Joint Ship Detection Based on Time-Frequency Domain and CFAR Methods with HF Radar.* Remote Sensing, 2021, 13(8), 1548. DOI 10.3390/rs13081548.

## Короткий зміст
Compact HF surface-wave radar (HFSWR) для ship surveillance страждає на wide beam-width + low spatial gain → traditional CFAR має низьку Pd. **Joint TF analysis + CFAR**: TF ridge extraction → CFAR test на samples ridges → **binary integration** для рішення "це судно".

## Алгоритм
1. **Time-frequency analysis** (likely STFT або CWT) сигналу
2. **TF ridge extraction** — лінії максимумів у TF
3. **CFAR detection** на samples кожного ridge
4. **Binary integration** — об'єднання per-sample рішень → per-ridge decision

## Валідація
OSMAR-SD (Ocean State Monitoring and Analyzing Radar) дані + AIS ship records як ground truth.

## Релевантність до проєкту
- **Stage 1+2** комбо: точно те що ми хочемо — STFT → CFAR (Stage 1) → integration (Stage 2 hint of ridge tracking)
- **Binary integration** — наша майбутня stratergy для DecisionFusion ([[11-latency-decision-fusion]])
- Архітектура "TF ridge → per-sample CFAR → integrate" дуже схожа на наш CFAR → Blind Estimator → Dechirp Verify

## Посилання
- [[08-stage1-oscfar-cpp]]
- [[03-tz2-dwt-cwt]] — теж TF analysis (Stage 2)
- [[11-latency-decision-fusion]] — Binary integration аналог
- [[ext-cfar-theory-01]] — TF-CFAR (теоретична база)
