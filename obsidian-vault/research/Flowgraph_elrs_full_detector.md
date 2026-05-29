# Flowgraph: `elrs_full_detector.grc`

---

## Загальна структура flowgraph (зліва направо)

```
SoapySDR Source
     ↓ (Complex float32, high sample rate)
OS_CFAR_2D Trigger (Stage 1)
     ↓ (Stream + Message port при виявленні енергії)
Message To Variable / Trigger Block
     ↓ (Message)
Blind Parameter Estimator (Stage 2 - DWT+CWT)
     ↓ (Message з SF, BW, Confidence)
Dechirp Matched Filter (Stage 3)
     ↓ (Message + optional stream)
NELoRa Neural Verifier (Stage 4)
     ↓ (Message)
Decision Fusion + Logger
     ↓
├── File Sink (PDU log)
├── UDP Sink (для передачі на іншу систему)
├── QT GUI Message Debug
└── Scope / Waterfall Sink (для візуалізації)
```

---

## Детальний опис блоків та з'єднань

| № | Блок | Тип | Категорія | Основні параметри | Примітки |
|---|------|-----|-----------|-------------------|----------|
| 1 | **Soapy SDR Source** | Source | SoapySDR | Sample Rate: 80e6 або 100e6, Center Freq: змінна, Bandwidth: 80 MHz, Device: Aaronia | Головне джерело |
| 2 | **OS_CFAR_2D** | General | elrs_detector | `guard_x=3`, `guard_y=2`, `train_x=12`, `train_y=8`, `rank_percent=0.75`, `threshold_db=11.0`, `nfft=1024`, `hop=256` | Stage 1 — найшвидший тригер |
| 3 | **Message Debug** | Sink | Debug | — | Для відлагодження Stage 1 |
| 4 | **Trigger / Message To Variable** | Utility | — | — | Активує наступні блоки |
| 5 | **Blind Parameter Estimator** | General (Python) | elrs_detector | `max_sf=12` | Stage 2 — видає SF і BW |
| 6 | **Dechirp Matched Filter** | General (C++/CUDA) | elrs_detector | `use_blind_params=True` | Stage 3 |
| 7 | **NELoRa Neural Verifier** | General (Python) | elrs_detector | `model_path=/models/nelora_efficientnet_b3.pt`, `confidence_threshold=0.65` | Stage 4 |
| 8 | **Decision Fusion** | General (Python) | elrs_detector | `fusion_mode=weighted` | Фінальне рішення |
| 9 | **QT GUI Message Debug** | Sink | Debug | — | Основний вивід |
| 10 | **UDP Sink** | Sink | Network | Host: 127.0.0.1, Port: 7355 | Передача на інші системи |
| 11 | **Waterfall Sink** + **QT GUI Time Sink** | Visualization | Qt GUI | — | Для візуального контролю |

---

## Рекомендована логіка з'єднань

**Stream path** (основний потік):  
`SoapySDR → OS_CFAR_2D → (thru) → Dechirp Matched Filter → (optional) → Null Sink або Scope`

**Message path** (основна логіка управління):
- `OS_CFAR_2D (msg out) → Message Trigger → Blind Parameter Estimator`
- `Blind Parameter Estimator (msg out) → Dechirp Matched Filter`
- `Dechirp Matched Filter (msg out) → NELoRa Neural Verifier`
- `NELoRa Neural Verifier → Decision Fusion → Message Debug + UDP Sink`

---

## Параметри змінних (Variables) у flowgraph

```
samp_rate = 100e6
center_freq = 915e6  (змінна)
trigger_threshold_db = 11.0
neural_conf_threshold = 0.65
enable_stage4 = True
```

---

## Рекомендації по оформленню flowgraph

1. Згрупуйте блоки по Stage (використовуйте **Block → Change Color**).
2. Додайте **Annotation** (текст) для кожного Stage.
3. Створіть **Hierarchical Block** для всього детектора в майбутньому.
4. Додайте **Variable Controls** (GUI) для:
   - Center Frequency
   - Trigger Threshold
   - Neural Confidence Threshold
   - Enable/Disable Neural Stage
