# ТЕХНІЧНЕ ЗАВДАННЯ №3
**Wigner-Hough Transform (WHT) для виявлення та аналізу чирп-сигналів ELRS**

**Дата:** 20 травня 2026  
**Пріоритет:** Середньо-Високий (аналітичний інструмент + потужний детектор для складних умов)  
**Мета:** Реалізувати Wigner-Hough Transform як точний метод автоматичного виявлення лінійних чирпів у часо-частотній площині, особливо ефективний для сліпої детекції ELRS/MiELRS/ZeLRS при низькому SNR.

---

## 1. Загальні вимоги

- Виявлення чирпів без априорної інформації про SF/BW.
- Робота при **SNR до -14…-16 dB**.
- Висока роздільність у просторі параметрів (нахил чирпа + часовий зсув).
- Використання як самостійного детектора та як верифікатора для інших методів.
- Підтримка GPU-прискорення.
- Латентність: **≤ 40 мс** на буфер 50–100 мс (допустимо вища, ніж у попередніх методах, оскільки це аналітичний інструмент).

---

## 2. Алгоритм (детальний опис)

**Теоретична основа:**  
Wigner-Ville Distribution (WVD) дає найкращу часо-частотну роздільність, але має перехресні члени. Hough Transform накопичує енергію прямих ліній (чирпів) у параметричному просторі (час-затримка vs частотний нахил).

### Етапи роботи

1. **Обчислення Wigner-Ville Distribution** (або Pseudo-WVD для зменшення перехресних членів).
2. **Hough Transform** у просторі параметрів чирпа:
   - Параметри: початкова частота `f0`, частотна швидкість `μ` (chirp rate).
3. **Пік-пошук** у Hough-акумуляторі.
4. **Витягнення параметрів** (SF, BW, час початку, CFO).
5. **Верифікація** знайдених чирпів через dechirping або CWT.

---

## 3. Вимоги до реалізації (з прикладами коду)

```python
import cupy as cp
import numpy as np
from numba import cuda, float32

class WignerHoughDetector:
    def __init__(self, nfft=1024, max_chirp_rate=500e3):
        self.nfft = nfft
        self.hough_accumulator = None
       
    def wvd(self, x: cp.ndarray) -> cp.ndarray:
        """Pseudo Wigner-Ville Distribution"""
        N = len(x)
        analytic = cp.signal.hilbert(x)  # Аналітичний сигнал
       
        wvd_matrix = cp.zeros((N//2, N), dtype=cp.float32)
       
        # Обчислюємо WVD з вікном (для зменшення артефактів)
        for tau in range(-self.nfft//4, self.nfft//4):
            idx = cp.arange(N - abs(tau))
            kernel = analytic[idx] * cp.conj(analytic[idx + abs(tau)])
            wvd_matrix[tau + self.nfft//4, idx] = cp.real(kernel)
       
        return wvd_matrix
   
    def hough_transform(self, wvd_matrix: cp.ndarray):
        """Hough Transform для чирпів"""
        height, width = wvd_matrix.shape
        # Параметричний простір: (rho - time offset, theta - chirp rate)
        theta_res = 180
        rho_res = width
       
        accumulator = cp.zeros((rho_res, theta_res), dtype=cp.float32)
       
        # CUDA kernel для прискорення (критично важливо!)
        @cuda.jit
        def hough_kernel(image, accum, cos_theta, sin_theta):
            i, j = cuda.grid(2)
            if i < image.shape[0] and j < image.shape[1]:
                if image[i, j] > 0:
                    for t in range(theta_res):
                        rho = int(j * cos_theta[t] + i * sin_theta[t])
                        if 0 <= rho < accum.shape[0]:
                            cuda.atomic.add(accum, (rho, t), image[i, j])
       
        # Підготовка кутів
        theta = cp.linspace(0, cp.pi, theta_res)
        cos_t = cp.cos(theta)
        sin_t = cp.sin(theta)
       
        # Запуск kernel...
        # (повна реалізація kernel буде в фінальному коді)
       
        return accumulator
   
    def detect(self, iq_signal: cp.ndarray):
        wvd_mat = self.wvd(iq_signal)
        hough_acc = self.hough_transform(wvd_mat)
       
        # Знаходимо максимуми
        max_val = cp.max(hough_acc)
        rho_max, theta_max = cp.unravel_index(cp.argmax(hough_acc), hough_acc.shape)
       
        estimated_chirp_rate = self._theta_to_chirp_rate(theta_max)
        estimated_sf_bw = self._parameters_to_sf_bw(estimated_chirp_rate)
       
        return {
            'detected': max_val > self.threshold,
            'confidence': float(max_val),
            'chirp_rate': estimated_chirp_rate,
            'estimated_sf': estimated_sf_bw['sf'],
            'estimated_bw': estimated_sf_bw['bw'],
            'time_offset': rho_max
        }
```

---

## 4. Метрики успіху

- Pd ≥ 90% при SNR = -14 dB
- Точність оцінки chirp rate: ±2%
- Точність визначення SF: ≥ 96%
- Час виконання WVD + Hough: ≤ 35 мс на RTX 3070 (з GPU оптимізацією)

---

## 5. Тестування

- Синтетичні чирпи з різними SF/BW, CFO, STO.
- Реальні записи ELRS з Aaronia (різні пульти).
- Тести з сильними завадами (WiFi, Bluetooth, кілька одночасних ELRS).
- Порівняння з Dechirping та DWT/CWT.
