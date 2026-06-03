---
tags: [stage-2, knowledge-builder, gnuradio, flowgraph, grc]
created: 2026-05-29
type: reference
stage: 2
status: done
source: Flowgraph_elrs_full_detector.md
drive_id: 1ccGdfr_5VpUjlFVlXtmmA61DnztHnK1M
---

# Flowgraph: `elrs_full_detector.grc`

---

## Загальна структура flowgraph (зліва направо)

```
SoapySDR Source
     ↓ (Complex float32, high sample rate)
OS_CFAR_2D Trigger (Stage 1)
     ↓ (Stream + Message port при виявленні)
Message To Variable / Trigger Block
     ↓ (Message)
Blind Parameter Estimator (Stage 2 — DWT+CWT)
     ↓ (Message з SF, BW, Confidence)
Dechirp Matched Filter (Stage 3)
     ↓ (Message + optional stream)
NELoRa Neural Verifier (Stage 4)
     ↓ (Message)
Decision Fusion + Logger
     ↓
├── File Sink (PDU log)
├── UDP Sink (127.0.0.1:7355)
├── QT GUI Message Debug
└── Waterfall / Scope Sink
```

---

## Детальний опис блоків

| № | Блок | Тип | Основні параметри |
|---|------|-----|-------------------|
| 1 | **Soapy SDR Source** | Source | SR: 80–100e6, CF: 915e6, BW: 80 MHz, Device: Aaronia |
| 2 | **OS_CFAR_2D** | C++ General | guard_x=3, guard_y=2, train_x=12, train_y=8, rank_percent=0.75, threshold_db=11.0, nfft=1024, hop=256 |
| 3 | **Message Debug** | Sink | Stage 1 відлагодження |
| 4 | **Blind Parameter Estimator** | Python General | max_sf=12 |
| 5 | **Dechirp Matched Filter** | C++/CUDA General | use_blind_params=True |
| 6 | **NELoRa Neural Verifier** | Python General | model_path=/models/nelora.pt, conf_threshold=0.65 |
| 7 | **Decision Fusion** | Python General | fusion_mode=weighted |
| 8 | **QT GUI Message Debug** | Sink | Основний вивід |
| 9 | **UDP Sink** | Sink | 127.0.0.1:7355 |
| 10 | **Waterfall + Time Sink** | Qt GUI | Візуальний контроль |

---

## Параметри змінних (Variables)

```
samp_rate = 100e6
center_freq = 915e6
trigger_threshold_db = 11.0
neural_conf_threshold = 0.65
enable_stage4 = True
```

---

## Логіка з'єднань

**Stream path:**
`SoapySDR → OS_CFAR_2D → Dechirp → Null Sink`

**Message path:**
- `OS_CFAR_2D (msg out) → Blind Parameter Estimator`
- `Blind (msg out) → Dechirp Matched Filter`
- `Dechirp (msg out) → NELoRa Verifier`
- `NELoRa → Decision Fusion → Message Debug + UDP`

---

## Рекомендації

1. Кольорове кодування блоків по Stage.
2. Annotation для кожного Stage.
3. GUI Variable Controls для: CF, threshold, confidence.
4. Hierarchical Block для всього детектора (фінальна версія).

---

## Посилання

- [[stage2-tz-gnuradio]] — ТЗ інтеграції
- [[stage2-oot-setup]] — покрокова інструкція
- [[10-gnuradio-flowgraph]] — базовий flowgraph (KB-2)
- [[08-stage1-oscfar-cpp]] — Stage 1 (закрито)
