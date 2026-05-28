---
tags: [knowledge-builder, code, stage4, nelora, onnx, neural, async]
created: 2026-05-28
type: code
stage: 4
status: ready
drive_id: 1SMbJRHAZALXmoRCKeMJ_6RbeMl7XUt_ZkKgY5dbCFQ8
source: 13_stage4_nelora_verifier_onnx.md
---

# Stage 4: nelora_verifier.py (ONNX Runtime + Async)

## Призначення
Production-ready Stage 4 верифікатор — ONNX Runtime + async queue, щоб не блокувати GNU Radio scheduler.

## Чому ONNX Runtime, а не PyTorch
- Швидший inference на GPU (CUDA EP оптимізований під продакшн)
- Не тягне torch у пам'ять
- Експорт з PyTorch/TF/JAX
- Стабільніший у багатопоточному GR

## API класу `NELoRa_Verifier`
```python
gr.basic_block(
    name="NELoRa Neural Verifier",
    in_sig=None, out_sig=None  # тільки message-based
)

# Параметри:
#   model_path="models/nelora_v1.onnx"
#   confidence_threshold=0.65
#   use_gpu=True (фоллбек на CPU)
#   max_queue_size=64
```

## Архітектура
- ORT InferenceSession з `CUDAExecutionProvider` (фоллбек `CPUExecutionProvider`)
- Async worker thread + `queue.Queue` (буфер запитів)
- Subscribe message port → подати у чергу → виконати inference → publish результат
- Защита: max_queue_size захищає від накопичення при overload

## Артефакти
- `python/elrs_detector/nelora_verifier.py`
- `models/nelora_v1.onnx` (експортується окремо)

## Залежності
- Імплементує [[05-tz4-nelora]]
- Координується через [[11-latency-decision-fusion]] (Fusion забирає вихід)
- Edge AI варіанти: [[16-edge-ai-fhss-tracker]] (TensorRT INT8, Coral TPU)
- RF fingerprinting через embeddings: [[15-rf-fingerprinting-tz]]
