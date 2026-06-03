---
tags: [stage-2, knowledge-builder, tz, dechirp, matched-filter, stage-3]
created: 2026-05-29
type: specification
stage: 3
status: done
source: TZ_01_Dechirping_Matched_Filter_Bank.md
drive_id: 1YL4wBhM_HV5fWyKAxmZ3UNfjZZtRKIkj
---

# ТЕХНІЧНЕ ЗАВДАННЯ №1
**Dechirping + Matched Filter Bank з підтримкою сліпої оцінки параметрів для детекції ELRS**

**Дата:** 20 травня 2026
**Пріоритет:** Високий (основний метод Stage 3)
**Мета:** Створити високоточний детектор преамбули ExpressLRS, здатний працювати в умовах невідомих SF, BW та hopping pattern.

---

## 1. Загальні вимоги

- Максимальна ймовірність детекції (**Pd**) при SNR від -15 dB.
- Підтримка **сліпої** роботи (без попереднього знання SF/BW).
- Сумісність з GNU Radio + Python/CUDA.
- Підготовка до перенесення на FPGA (ADRV9009).
- Латентність етапу: **≤ 25 мс** при обробці 80–100 MS/s.

---

## 2. Алгоритм (детальний опис)

### Етапи роботи

**1. Генерація еталонних чирпів**
- Генерувати up-chirp і down-chirp для всіх комбінацій:
  - SF: 7, 8, 9, 10, 11, 12
  - BW: 203, 406, 812, 1625 kHz
- Зберігати в пам'яті як комплексні масиви.

**2. Dechirping**
- Для кожного можливого SF/BW:
  `y_dechirped = x_received * conj(reference_upchirp)`
- Після dechirping чирп стає синусоїдою з постійною частотою.

**3. Matched Filtering**
- Виконати кореляцію (або FFT-based multiplication) з еталонним шаблоном.
- Шукати **піки**, які повторюються з інтервалом символу.

**4. Сліпа оцінка параметрів**
- Виконувати паралельно для кількох SF/BW.
- Вибирати комбінацію з максимальною енергією піків.

**5. CFO / STO корекція**
- Оцінка Carrier Frequency Offset за позицією піку після dechirping.
- Ітеративна корекція.

---

## 3. Реалізація

```python
import cupy as cp
import numpy as np

class ELRS_Dechirp_MatchedFilter:
    def __init__(self, max_sf=12, target_snr_db=-15):
        self.sfs = list(range(7, max_sf+1))
        self.bws = [203000, 406000, 812000, 1625000]
        self.reference_chirps = self._generate_all_references()
        self.stream = cp.cuda.Stream(non_blocking=True)

    def _generate_chirp(self, sf, bw, up=True):
        N = 2**sf
        freq = cp.linspace(-bw/2, bw/2, N) if up else cp.linspace(bw/2, -bw/2, N)
        phase = cp.cumsum(2 * cp.pi * freq / bw)
        return cp.exp(1j * phase)

    def detect(self, iq_signal: cp.ndarray) -> dict:
        best_score = 0
        best_params = None
        for sf in self.sfs:
            for bw in self.bws:
                ref_up = self.reference_chirps[(sf, bw, 'up')]
                dechirped = iq_signal[:len(ref_up)] * cp.conj(ref_up)
                spectrum = cp.abs(cp.fft.fft(dechirped))
                peak_value = cp.max(spectrum)
                score = peak_value / cp.mean(spectrum)
                if score > best_score:
                    best_score = score
                    best_params = {'sf': sf, 'bw': bw, 'cfo': int(cp.argmax(spectrum))}
        return {'detected': best_score > self.threshold, 'score': float(best_score), 'params': best_params}
```

---

## 4. Метрики успіху

| Метрика | Ціль |
|---------|------|
| Pd | ≥ 95% при SNR = -12 dB |
| Pd | ≥ 80% при SNR = -16 dB |
| Pfa | ≤ 0.1% |
| Latency | < 20 мс на 50 мс буфері (RTX 3070) |

---

## 5. Тестування

- Синтетичні сигнали (з різним SNR, CFO, STO).
- Реальні записи з Aaronia + стенд з атенюаторами.
- Змішування з завадами (WiFi, інший ELRS, шум).
- Тест на MiELRS / ZeLRS (з phase reversal тощо).

---

## Посилання

- [[02-tz1-dechirp-mf]] — аналіз TZ#1 (KB-2)
- [[stage2-dechirp-math]] — математика dechirping та ортогональність
- [[stage2-dechirp-queries]] — дослідницькі запити
- [[stage2-tz-dwt-cwt]] — Stage 2 (параметри для Stage 3)
- [[docs/stage2-plan]] — план Stage 2
