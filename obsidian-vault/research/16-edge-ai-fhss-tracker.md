---
tags: [knowledge-builder, tz, edge-ai, jetson, coral, fhss, tracker, jammer]
created: 2026-05-28
type: tz
stage: 4-edge
status: approved
version: "1.0"
drive_id: 1UA9q7uiAkaFfMMbYVucseOjUS8kWYI1pwW2sQR1Kp9o
source: 16_edge_ai_fhss_tracker_tz.md
---

# ТЗ: Edge AI Deployment + FHSS Tracker

## Два модулі в одному ТЗ
1. **Edge AI Deployment** — Stage 4 + RF Fingerprinting на embedded (≤15 ms, ≤8 W)
2. **FHSS Tracker** — передбачення наступної частоти стрибка → завада ДО приходу пакету

## Edge AI: підтримувані платформи
| Платформа | Engine | Quant | Latency | Power |
|-----------|--------|-------|---------|-------|
| Jetson Orin Nano | TensorRT 8.6 | FP16/INT8 | 8-12 ms | 7-10 W |
| Google Coral USB/PCIe | Edge TPU | INT8 | 6-10 ms | 2-4 W |
| Khadas VIM3 / RPi5+Hailo | HailoRT/TFLite | INT8 | 10-18 ms | 5-8 W |
| Artix-7+MicroBlaze (HLS) | Custom IP | Fixed-point | 3-6 ms | 2-4 W |

## Програмний стек
- `pybind11` / `nanobind` для C++/Python bridge
- `ZeroMQ` + MessagePack/FlatBuffers
- YAML config з hot-reload
- Prometheus + systemd watchdog

## C++ Inference API
```cpp
class EdgeAIInference {
    static std::unique_ptr<EdgeAIInference> create(model_path, backend="tensorrt");
    struct Result {
        bool detected;
        float confidence;
        int sf;
        float bw_hz;
        std::string device_fingerprint;
    };
    Result infer(const std::vector<std::complex<float>>& iq);
};
```

## FHSS Tracker (проактивна завада)
- Реверс LFSR / cyclostationarity для отримання hop pattern
- Стан машини hop tracking → передбачення наступної частоти
- Випереджаюча команда генератору завад (AD9910 / ADRV9009 TX)
- Цільова latency: <2 ms від детекції попереднього хопу до tuning заваді

## Цілі точності
- Stage 4 на edge: ≥85% (vs 95% на full GPU) при ≤15 ms
- FHSS prediction accuracy: ≥80% наступного хопу

## Залежності
- Edge форма [[13-stage4-nelora-verifier-onnx]]
- Edge форма [[15-rf-fingerprinting-tz]]
- HW варіант [[12-adrv9009-artix7-migration]]
- Виходить з [[14-commercial-defence-analysis]]
