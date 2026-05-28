---
tags: [knowledge-builder, code, stage2, python, cupy, dwt, cwt]
created: 2026-05-28
type: code
stage: 2
status: ready
drive_id: 1m99f1Ip6XcGcW9gveQ0g4_2csKA39p92L8q4miUBzB4
source: 09_stage2_blind_estimator_py.md
---

# Stage 2: blind_estimator.py + CUDA Kernel для OS-CFAR

## Призначення
Python-блок GNU Radio (`gr.sync_block`) для сліпої оцінки параметрів (SF/BW) ELRS сигналів.
Отримує тригери від OS-CFAR (Stage 1) через message port → виконує DWT + CWT аналіз → видає оцінку.

## API класу `Blind_Parameter_Estimator`
```python
gr.sync_block(
    name="Blind Parameter Estimator",
    in_sig=[np.complex64],
    out_sig=None,  # повідомлення через message port
)

# Параметри:
#   sample_rate=2e6
#   max_sf=12
#   snr_threshold=-15 (dB)
#   use_gpu=True (CuPy fallback to NumPy)
```

## Pipeline всередині блоку
1. Subscribe message port (тригер від Stage 1)
2. Прочитати ~50 ms IQ навколо піку
3. **DWT pre-screen** (pywt) → top-2 candidate SFs
4. **CWT refinement** (для candidate SFs, Morlet) → BW
5. Confidence gate → publish PMT з {sf, bw, confidence}

## Залежності runtime
- `pmt`, `pywt`, `scipy.fft`, `scipy.signal`
- Optional: `cupy` (GPU acceleration)

## Зв'язок
- Реалізує [[03-tz2-dwt-cwt]]
- Слухає Stage 1: [[08-stage1-oscfar-cpp]]
- Виходить у Stage 3 [[02-tz1-dechirp-mf]]
- Інтегрується через [[07-oot-gnuradio-skeleton]] / [[10-gnuradio-flowgraph]]
