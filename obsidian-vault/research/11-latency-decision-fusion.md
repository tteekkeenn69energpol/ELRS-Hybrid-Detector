---
tags: [knowledge-builder, code, optimization, latency, fusion, scheduling]
created: 2026-05-28
type: code
stage: all
status: ready
drive_id: 17-FabGLcOmjwcgQdsqT1HuNah1gQXHUv6hEae02W12E
source: 11_latency_decision_fusion.md
---

# Latency Optimization + Decision Fusion

## Призначення
Як запустити 80-100 MS/s через ланцюжок Python/C++ блоків GNU Radio без dropped samples + код Decision Fusion (weighted voting + hysteresis).

## Частина 1: Latency optimization
### 1. Vector sizes (критично)
- SoapySDR Source: `Vec Len = 8192 | 16384`
- OS_CFAR_2D (C++): `Vec Len = 4096`
- Python blocks (Stage 2,4): `Vec Len = 1 | 1024`

### 2. Real-Time Scheduling (Linux)
```bash
sudo chrt -f 90 gnuradio-companion
# або:
sudo chrt -f 90 -p <PID>
```

### 3. Threading
- `Thread Policy = Thread Per Block`
- `Max N Output Items = 0` (auto) або `32768`
- CPU affinity для важких блоків через `set_processor_affinity`

### 4. Tag propagation
- Stage 2-4 у Message Mode → НЕ підключати out_sig Stage 1 далі
- Або: `Tagged Stream Mux`

## Частина 2: DecisionFusion (`python/elrs_detector/decision_fusion.py`)
- Клас `gr.sync_block`
- Weighted Voting: ваги Stage 1-4 (наприклад CFAR=0.2, Dechirp=0.4, NN=0.3, Estim=0.1)
- Hysteresis: гістерезис на confidence (підтримка/гасіння детекції)
- Stage 4 (NN) може бути overruled якщо інші впевнені — захист від помилок NN на нових типах завад

## Залежності
- Завершує [[06-tz5-hybrid-pipeline]]
- Запускається з [[10-gnuradio-flowgraph]]
- Координує всі Stage 1-4
