# ТЕХНІЧНЕ ЗАВДАННЯ: Інтеграція гібридного ELRS-детектора з GNU Radio

**Дата:** 20 травня 2026  
**Мета:** Повна, стабільна та зручна інтеграція Multi-Stage Pipeline (Stage 1–5) у GNU Radio 3.10+ як готового OOT-модуля (Out-Of-Tree) для реального часу роботи з Aaronia Spectran V6 через SoapySDR.

---

## 1. Загальна Архітектура Інтеграції

```
SoapySDR Source (Aaronia)
        ↓
   [Stage 1: 2D OS-CFAR Trigger]     ← Python Block / C++ Block
        ↓ (Message або Tagged Stream при виявленні)
   [Stage 2: Blind Parameter Estimator]
        ↓
   [Stage 3: Dechirping + Matched Filter]
        ↓
   [Stage 4: Neural Verification]     ← Torch / ONNX
        ↓
   Message Sink / PDU → File / UDP / Display
```

---

## 2. Структура OOT-модуля

**Назва модуля:** `gr-elrs_detector`

```
gr-elrs_detector/
├── CMakeLists.txt
├── include/
│   └── elrs_detector/
├── lib/
│   ├── os_cfar_impl.cc          (C++ для Stage 1)
│   ├── blind_estimator_impl.cc
│   └── ...
├── python/
│   ├── elrs_detector/
│   │   ├── __init__.py
│   │   ├── os_cfar.py
│   │   ├── dechirp_detector.py
│   │   └── nelora_nn.py
│   └── bindings/
├── examples/
│   └── elrs_full_pipeline.grc
├── apps/
└── docs/
```

---

## 3. Детальний розпис блоків

### Блок 1: OS_CFAR_2D (Stage 1)
- Тип: **General Block** (C++ для максимальної швидкості)
- Вхід: Complex Float32 stream
- Вихід: Complex Float32 stream + Message port (при виявленні)
- Параметри (змінювані під час роботи):
  - `threshold_db`, `guard_x/y`, `train_x/y`, `rank_percent`
  - `nfft`, `hop_size`

### Блок 2: Blind_Parameter_Estimator (Stage 2)
- Тип: **Python Block** (sync_block)
- Активується повідомленням від Stage 1
- Виконує DWT + CWT
- Вихід: PDU з параметрами (`sf`, `bw`, `confidence`)

### Блок 3: Dechirp_MatchedFilter (Stage 3)
- Тип: **Hybrid** (C++/CuPy)
- Використовує параметри з Stage 2
- Підтримка банку шаблонів

### Блок 4: NELoRa_Neural_Verifier (Stage 4)
- Тип: **Python Block**
- Використовує Torch JIT / ONNX Runtime
- Підтримка GPU inference

---

## 4. Приклад реалізації Python Block (Stage 2)

```python
import pmt
import numpy as np
from gnuradio import gr
import cupy as cp
from .blind_estimator import ELRS_BlindParameterEstimator

class Blind_Parameter_Estimator(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="Blind Parameter Estimator",
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        self.estimator = ELRS_BlindParameterEstimator()
        self.set_output_multiple(1024)
       
        # Message port
        self.message_port_register_out(pmt.intern("parameters"))
   
    def work(self, input_items, output_items):
        in0 = input_items[0]
       
        # Обробка тільки при тригері (або постійно з low duty cycle)
        if self.triggered:
            result = self.estimator.estimate(cp.asarray(in0[0]))
           
            # Відправка PDU
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

## 5. Приклад GNU Radio Flowgraph

```
SoapySDR Source → OS_CFAR_2D → [Message Trigger]
При виявленні → Message to Variable → Blind_Parameter_Estimator
Blind → Dechirp_MatchedFilter
Dechirp → NELoRa_Verifier
Всі етапи мають Message Debug + File Sink для логів
```

---

## 6. Вимоги до тестування інтеграції

**Тест 1: End-to-End Latency**
- Вимірювання часу від SoapySDR Source до фінального PDU.

**Тест 2: Реал-тайм стабільність**
- 30 хвилин безперервної роботи на 80–100 MS/s без dropped samples.

**Тест 3: Cross-Stage Verification**
- Логування: який Stage виявив, який підтвердив, остаточний confidence.

**Тест 4: Зміна параметрів на льоту**
- Зміна threshold, nfft, hop_size під час роботи flowgraph.
