---
tags: [stage-2, knowledge-builder, tz, gnuradio, oot, integration]
created: 2026-05-29
type: specification
stage: 2
status: done
source: TZ_06_GNU_Radio_Integration.md
drive_id: 1Cl6UR8TFbRGHj0GOCX4azVvtD488f9UV
---

# ТЕХНІЧНЕ ЗАВДАННЯ: Інтеграція гібридного ELRS-детектора з GNU Radio

**Дата:** 20 травня 2026
**Мета:** Повна, стабільна та зручна інтеграція Multi-Stage Pipeline (Stage 1–5) у GNU Radio 3.10+ як готового OOT-модуля `gr-elrs_detector`.

---

## 1. Загальна Архітектура Інтеграції

```
SoapySDR Source (Aaronia)
        ↓
   [Stage 1: 2D OS-CFAR Trigger]     ← C++ Block
        ↓ (Message при виявленні)
   [Stage 2: Blind Parameter Estimator]  ← Python Block
        ↓ PDU {sf, bw, confidence}
   [Stage 3: Dechirping + Matched Filter]  ← C++/CuPy
        ↓
   [Stage 4: Neural Verification]     ← Python/ONNX
        ↓
   Message Sink / PDU → File / UDP / Display
```

---

## 2. Структура OOT-модуля `gr-elrs_detector`

```
gr-elrs_detector/
├── CMakeLists.txt
├── include/elrs_detector/
├── lib/
│   ├── os_cfar_impl.cc          (C++ для Stage 1)
│   ├── blind_estimator_impl.cc
│   └── dechirp_matched_impl.cc
├── python/elrs_detector/
│   ├── __init__.py
│   ├── blind_estimator.py
│   ├── nelora_nn.py
│   └── decision_fusion.py
├── python/bindings/
├── examples/elrs_full_pipeline.grc
└── docs/
```

---

## 3. Блоки OOT

### Блок 2: Blind_Parameter_Estimator (Stage 2)
- Тип: **Python Block** (sync_block)
- Активується повідомленням від Stage 1
- Виконує DWT + CWT
- Вихід: PDU `{sf, bw, confidence}`

```python
import pmt, numpy as np
from gnuradio import gr
import cupy as cp
from .blind_estimator import ELRS_BlindParameterEstimator

class Blind_Parameter_Estimator(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self, name="Blind Parameter Estimator",
            in_sig=[np.complex64], out_sig=[np.complex64])
        self.estimator = ELRS_BlindParameterEstimator()
        self.set_output_multiple(1024)
        self.message_port_register_out(pmt.intern("parameters"))

    def work(self, input_items, output_items):
        in0 = input_items[0]
        if self.triggered:
            result = self.estimator.estimate(cp.asarray(in0[0]))
            pdu = pmt.make_dict()
            pdu = pmt.dict_add(pdu, pmt.intern("sf"), pmt.from_long(result['sf']))
            pdu = pmt.dict_add(pdu, pmt.intern("bw"), pmt.from_float(result['bw']))
            pdu = pmt.dict_add(pdu, pmt.intern("confidence"), pmt.from_float(result['confidence']))
            self.message_port_pub(pmt.intern("parameters"), pdu)
            self.triggered = False
        output_items[0][:] = in0
        return len(output_items[0])
```

---

## 4. Вимоги до тестування інтеграції

- **Тест 1:** End-to-End Latency — від SoapySDR до фінального PDU.
- **Тест 2:** Реал-тайм стабільність — 30 хв на 80–100 MS/s без dropped samples.
- **Тест 3:** Cross-Stage Verification — логування кожного Stage.
- **Тест 4:** Зміна параметрів на льоту.

---

## Посилання

- [[07-oot-gnuradio-skeleton]] — OOT skeleton (KB-2)
- [[stage2-oot-setup]] — покрокова інструкція створення OOT
- [[stage2-flowgraph]] — приклад flowgraph
- [[stage2-tz-dwt-cwt]] — Stage 2 spec
- [[ext-github-gnuradio-32]] — gr-cuda (zero-copy GPU buffer)
