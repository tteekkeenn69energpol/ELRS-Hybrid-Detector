# ТЕХНІЧНЕ ЗАВДАННЯ №5
**Розробка повного гібридного реал-тайм детектора ExpressLRS (Multi-Stage Pipeline)**

**Замовник:** Tekken Corp. Defense Tech Division  
**Дата:** 20 травня 2026  
**Виконавець:** Стороння компанія-розробник (GPU + SDR + Signal Processing team)  
**Мета:** Створити **промисловий рівень** гібридну систему детекції невідомих ELRS/MiELRS/ZeLRS сигналів з максимальною ймовірністю виявлення в умовах реального ефіру.

---

## 1. Загальна Архітектура Системи (Multi-Stage Pipeline)

Система повинна працювати за принципом **cascaded detection** (каскадне виявлення):

```
Stage 0 – Signal Acquisition
SoapySDR (Aaronia) / ADRV9009 → CUDA Pinned Memory

Stage 1 – Fast Wideband Trigger (2D OS-CFAR)
Stage 2 – Blind Parameter Estimation (DWT + CWT/SST)
Stage 3 – Fine Detection (Dechirping + Matched Filter Bank)
Stage 4 – Deep Neural Verification (NELoRa-style CNN/Transformer)
Stage 5 – Decision Fusion & Tracking
```

---

## 2. Детальний розпис етапів розробки

### Етап 1: Проєктування та Прототипування (4 тижні)

- Розробити детальну блок-схему всього pipeline з зазначенням latency кожного етапу.
- Створити **Unified Configuration Manager** (JSON/YAML) для динамічної зміни параметрів без перезапуску.
- Реалізувати **Stage 1: 2D OS-CFAR** (повністю на GPU, CuPy/Numba).
- Deliverables:
  - Код Stage 1 з профілюванням (time, memory, occupancy).
  - Тестовий flowgraph у GNU Radio.
  - Звіт з throughput (MS/s) на RTX 3070.

**Тестування Етапу 1:**
- Синтетичний шум + ELRS сигнали на рівні -6…-10 dB.
- Метрика: Pd > 98%, Pfa < 0.5% при 100 MS/s.

### Етап 2: Blind Parameter Estimation (3–4 тижні)

- Реалізувати **Stage 2** (DWT + CWT/SST).
- Інтеграція зі Stage 1.
- Deliverables:
  - Модуль `BlindEstimator` з методом `.estimate(iq_buffer)`.
  - Точність SF ≥ 97%, BW ≥ 95% при SNR -12 dB.

**Тестування:**
- 5000 синтетичних записів (всі комбінації SF7–12 × BW).
- Реальні записи з Aaronia + стенд (атенюатори + змішувач завад).

### Етап 3: Fine Detection (4 тижні)

- Повна реалізація **Stage 3** (Dechirping + Matched Filter Bank).
- Підтримка сліпої роботи через результати Stage 2.
- CFO/STO корекція в реальному часі.
- Deliverables: модуль `DechirpDetector` з детальним логуванням піків.

**Тестування:**
- SNR sweep від -5 до -18 dB.
- Тести з phase reversal (MiELRS/ZeLRS).
- Метрика: Pd ≥ 93% при SNR = -14 dB.

### Етап 4: Neural Verification (5–6 тижнів)

- Розробка та навчання **Stage 4** (NELoRa-style мережа).
- Multi-task навчання (detection + SF + BW).
- Transfer learning + fine-tuning на власному датасеті.
- Deliverables:
  - ONNX + TorchScript версії моделі.
  - Inference pipeline на GPU ≤ 8 мс.

**Тестування:**
- Cross-validation на unseen пультах.
- Тести з комбінованими завадами (WiFi + Bluetooth + 2–3 ELRS).
- Pd ≥ 90% при SNR = -17 dB.

### Етап 5: Інтеграція, Fusion та Оптимізація (4 тижні)

- Створити **Decision Fusion Engine** (weighted voting + hysteresis).
- Реалізувати end-to-end pipeline з CUDA Streams.
- Оптимізація під RTX 3070 + підготовка до FPGA.
- Deliverables:
  - Повний Python пакет `elrs_detector`.
  - GNU Radio OOT блок.
  - Детальний Performance Report.

---

## 3. Загальні вимоги до всього проєкту

- **Мова:** Python 3.10+, CUDA 12.x, PyTorch 2.4+
- **Код:** чистий, модульний, з typing та документацією.
- **Профілювання:** кожен kernel + етап повинен мати вбудований таймер.
- **Конфігурація:** всі параметри (thresholds, nfft, hop тощо) виносяться в config.
- **Тестування:** Unit + Integration + System tests + реальні стендові тести.

---

## 4. Приймальні випробування (Final Acceptance Criteria)

1. Стабільна робота на **100 MS/s** без dropped samples протягом 30 хвилин.
2. Pd ≥ 95% при SNR = -12 dB на реальних сигналах.
3. Pd ≥ 80% при SNR = -16 dB з завадами.
4. Загальна Pfa ≤ 0.1%.
5. Повна документація + приклади запуску.
