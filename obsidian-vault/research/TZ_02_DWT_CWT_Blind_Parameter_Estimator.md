# ТЕХНІЧНЕ ЗАВДАННЯ №2
**DWT + CWT based Blind Parameter Estimator для сліпої оцінки SF та BW в ELRS**

**Дата:** 20 травня 2026  
**Пріоритет:** Високий (Stage 2 — Blind Parameter Estimation)  
**Мета:** Створити швидкий та надійний модуль, який без попереднього знання параметрів визначає Spreading Factor (SF) та Bandwidth (BW) сигналу ExpressLRS, навіть у складних умовах завад.

---

## 1. Загальні вимоги

- Повністю **сліпа** робота (немає априорної інформації про SF/BW).
- Висока швидкість — має працювати як **попередній етап** перед Dechirping.
- Стійкість до SNR від -14 dB.
- Підтримка основних ELRS діапазонів: 433/868/915/2.4 GHz.
- Підготовка до перенесення на FPGA (ADRV9009).
- Латентність: **≤ 15 мс** на буфер 50–100 мс.

---

## 2. Алгоритм (детальний опис)

**Основна ідея:**
- DWT використовується для швидкого грубого визначення SF через **унікальну періодичність вейвлет-коефіцієнтів**.
- CWT (з вейвлетами Morlet/Morse) використовується для точного визначення BW та локалізації чирпів.

### Етапи роботи

**1. Попередня обробка**
- Нормалізація потужності сигналу.
- Груба корекція CFO (опціонально через autocorr).

**2. DWT-based SF Estimation**
- Використовувати Discrete Wavelet Transform (Daubechies або Symlet wavelet).
- Аналізувати **періодичність** детальних коефіцієнтів на різних рівнях розкладання.
- Кожен SF має характерну структуру періодичності вейвлет-коефіцієнтів.

**3. CWT-based BW Estimation**
- Обчислення Continuous Wavelet Transform з Morlet wavelet.
- Пошук максимальної концентрації енергії в масштабі, що відповідає BW.
- Використання Synchrosqueezing (SST) для покращення роздільності.

**4. Верифікація**
- Комбінований score з DWT + CWT.
- Підтвердження наявності чирп-подібної структури.

---

## 3. Вимоги до реалізації (з прикладами коду)

```python
import cupy as cp
import numpy as np
import pywt
from ssqueezepy import cwt, ssq_cwt  # для Synchrosqueezing

class ELRS_BlindParameterEstimator:
    def __init__(self):
        self.sfs = list(range(7, 13))
        self.bws = [203000, 406000, 812000, 1625000]
        self.wavelet = 'sym5'          # або 'db4', 'sym8'
        self.dt = 1.0 / 100e6          # приклад для 100 MS/s
       
    def dwt_sf_estimation(self, iq_signal: np.ndarray) -> dict:
        # Перетворюємо в реальну частину або magnitude
        signal = np.abs(iq_signal)
       
        sf_scores = {}
        for sf in self.sfs:
            # Теоретична довжина символу
            symbol_len = 2 ** sf
           
            # Багаторівневе DWT
            coeffs = pywt.wavedec(signal, self.wavelet, level=6)
           
            # Аналіз періодичності в детальних коефіцієнтах
            detail = coeffs[1]  # high-frequency details
            autocorr = np.correlate(detail, detail, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
           
            # Шукаємо пік біля symbol_len
            peak_score = self._find_periodic_peak(autocorr, symbol_len)
            sf_scores[sf] = peak_score
       
        best_sf = max(sf_scores, key=sf_scores.get)
        return {'sf': best_sf, 'score': sf_scores[best_sf]}
   
    def cwt_bw_estimation(self, iq_signal: cp.ndarray):
        # Використовуємо Synchrosqueezed CWT
        W, scales = ssq_cwt(iq_signal, wavelet='morlet')
       
        # Знаходимо масштаб з максимальною енергією
        energy = cp.abs(W).mean(axis=1)
        best_scale_idx = cp.argmax(energy)
        estimated_bw = self._scale_to_bw(scales[best_scale_idx])
       
        return {'bw': estimated_bw, 'cwt_energy': float(energy[best_scale_idx])}
   
    def estimate(self, iq_signal):
        # Паралельне виконання
        dwt_result = self.dwt_sf_estimation(iq_signal.get() if isinstance(iq_signal, cp.ndarray) else iq_signal)
        cwt_result = self.cwt_bw_estimation(cp.asarray(iq_signal))
       
        return {
            'sf': dwt_result['sf'],
            'bw': cwt_result['bw'],
            'confidence': (dwt_result['score'] + cwt_result['cwt_energy']) / 2,
            'method': 'DWT_CWT'
        }
```

---

## 4. Метрики успіху

- Точність визначення SF: ≥ 98% при SNR ≥ -10 dB
- Точність визначення BW: ≥ 95% при SNR ≥ -12 dB
- Загальна точність пари (SF + BW): ≥ 92% при SNR = -14 dB
- Час виконання: ≤ 12 мс на 50 мс буфер (RTX 3070)

---

## 5. Тестування

- Синтетичні сигнали з усіма комбінаціями SF/BW.
- Реальні записи з Aaronia (різні пульти, потужності, атенюація).
- Тести зі змішаними завадами (WiFi, Bluetooth, інший ELRS, Gauss noise).
- Тести на MiELRS / ZeLRS (з модифікованою преамбулою).
