---
tags: [stage-2, knowledge-builder, tz, wigner, hough, chirp-detection]
created: 2026-05-29
type: specification
stage: 2
status: done
source: TZ_03_Wigner_Hough_Transform.md
drive_id: 1LrqvgDDFHR0f7ODkmzZOMr00cKVKsXgD
---

# ТЕХНІЧНЕ ЗАВДАННЯ №3
**Wigner-Hough Transform (WHT) для виявлення та аналізу чирп-сигналів ELRS**

**Дата:** 20 травня 2026
**Пріоритет:** Середньо-Високий (аналітичний інструмент + потужний детектор для складних умов)
**Мета:** Реалізувати Wigner-Hough Transform як точний метод автоматичного виявлення лінійних чирпів у часо-частотній площині.

---

## 1. Загальні вимоги

- Виявлення чирпів без априорної інформації про SF/BW.
- Робота при **SNR до -14…-16 dB**.
- Висока роздільність у просторі параметрів (нахил чирпа + часовий зсув).
- Використання як самостійного детектора та як верифікатора.
- Підтримка GPU-прискорення.
- Латентність: **≤ 40 мс** на буфер 50–100 мс.

---

## 2. Алгоритм

**Теоретична основа:**
- Wigner-Ville Distribution (WVD) — найкраща часо-частотна роздільність, але має перехресні члени.
- Hough Transform накопичує енергію прямих ліній у параметричному просторі (chirp rate, time offset).

### Етапи роботи

1. **Wigner-Ville Distribution** (або Pseudo-WVD для зменшення перехресних членів).
2. **Hough Transform** у просторі параметрів чирпа: `f0`, `μ` (chirp rate).
3. **Пік-пошук** у Hough-акумуляторі.
4. **Витягнення параметрів** (SF, BW, час початку, CFO).
5. **Верифікація** через dechirping або CWT.

---

## 3. Реалізація

```python
import cupy as cp
from numba import cuda, float32

class WignerHoughDetector:
    def __init__(self, nfft=1024, max_chirp_rate=500e3):
        self.nfft = nfft

    def wvd(self, x: cp.ndarray) -> cp.ndarray:
        N = len(x)
        analytic = cp.signal.hilbert(x)
        wvd_matrix = cp.zeros((N//2, N), dtype=cp.float32)
        for tau in range(-self.nfft//4, self.nfft//4):
            idx = cp.arange(N - abs(tau))
            kernel = analytic[idx] * cp.conj(analytic[idx + abs(tau)])
            wvd_matrix[tau + self.nfft//4, idx] = cp.real(kernel)
        return wvd_matrix

    def detect(self, iq_signal: cp.ndarray):
        wvd_mat = self.wvd(iq_signal)
        hough_acc = self.hough_transform(wvd_mat)
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

| Метрика | Ціль |
|---------|------|
| Pd | ≥ 90% при SNR = -14 dB |
| Chirp rate accuracy | ±2% |
| SF accuracy | ≥ 96% |
| WVD + Hough latency | ≤ 35 мс (RTX 3070) |

---

## 5. Статус у архітектурі

WHT є **опціональним верифікатором** — не в основному шляху Stage 2 (занадто дорогий для real-time). Корисний для:
- Offline аналізу складних сигналів
- Верифікації при confidence < 0.4 у Stage 4

---

## Посилання

- [[04-tz3-wigner-hough]] — аналіз WHT (KB-2)
- [[stage2-tz-dwt-cwt]] — основний Stage 2
- [[stage2-key-confidence-gate]] — коли включати WHT
- [[docs/stage2-plan]] — план Stage 2
