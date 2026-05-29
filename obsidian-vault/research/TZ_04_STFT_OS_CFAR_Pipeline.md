# ТЕХНІЧНЕ ЗАВДАННЯ №4
**Розробка високопродуктивного GPU-акселерованого конвеєра STFT + 2D OS-CFAR для реал-тайм детекції преамбул ExpressLRS**

**Дата:** 19 травня 2026  
**Замовник:** Tekken Corp. Defense Tech Division  
**Виконавець:** Стороння компанія-розробник  
**Рівень:** Senior CUDA / GPU Engineer

---

## 1. Мета проєкту

Створити **максимально швидкий** і стабільний ланцюжок обробки сигналу на GPU для реального часу виявлення преамбул ExpressLRS (LoRa-based) на апаратурі Aaronia Spectran V6 з використанням SoapySDR.

**Цільова продуктивність:**
- Стабільна обробка **100 MS/s** (бажано 120+ MS/s) на RTX 3070.
- End-to-end latency від I/Q до видачі детекції **≤ 35 мс**.
- Zero dropped samples при тривалій роботі.

---

## 2. Архітектура конвеєра (обов'язкова)

```
SoapySDR Source (Aaronia) → CUDA Pinned Memory (cudaHostAlloc)
        ↓
GPU STFT Kernel (cuFFT + Custom Overlap-Add)
        ↓
Magnitude² + log10 (in dB) → Spectrogram
        ↓
GPU 2D OS-CFAR Kernel
        ↓
Peak Detection + Connected Components (optional)
        ↓
Message Sink (Time, Freq, SNR, Confidence, Estimated SF)
```

---

## 3. Детальні вимоги до GPU STFT Kernel

### 3.1. Технічні параметри

- Підтримувані `nfft`: **512, 1024, 2048, 4096**
- Overlap: **50% – 87.5%** (hop_size = nfft // 2, nfft // 4, nfft // 8)
- Вікна: Blackman-Harris (основне), Hann, Kaiser(β=8), Flat-top
- Формат даних: `complex64`

### 3.2. Обов'язкові техніки CUDA оптимізації

**Kernel параметри (конкретні рекомендації):**
- **Block Size**: `(256, 1, 1)` або `(128, 8, 1)` — залежно від nfft
- **Grid Size**: динамічно `(num_frames, 1, 1)`
- **Shared Memory**:
  - Для nfft=1024: мінімум **4–6 KB** на блок (window + input tile)
  - Для nfft=2048: **8–12 KB**
- **cuFFT Plan**: створювати один раз на старті, використовувати `cufftExecC2C`
- **Async Operations**: використовувати `cudaStream_t` (multiple streams — 4–8)
- **Memory Coalescing**: 100% coalesced global memory access
- **Register Pressure**: максимум 64 registers per thread

**Оптимізації вищого рівня:**
- Використовувати **cuFFT + custom kernel** для windowing та overlap-add.
- Batch processing: обробляти 4–8 spectrogram frames одночасно.
- Pinned Memory + Async memcpy.
- Zero-copy де можливо.

---

## 4. Детальні вимоги до 2D OS-CFAR Kernel

- Повністю на GPU (без копіювання spectrogram в RAM).
- Підтримка **2D rank filter** (Ordered Statistic).
- Параметри:
  - `guard_x`, `guard_y`
  - `train_x`, `train_y`
  - `rank_percent` (0.5 – 0.95)
  - `threshold_db` (адаптивний + фіксований)
- Вихід: бінарна detection map + SNR map (float32)

**Оптимізації:**
- Використовувати shared memory + sorting network або bitonic sort для маленьких вікон.
- Для великих вікон — radix sort або thrust::sort.

---

## 5. Вимоги до продуктивності (KPI)

| Параметр | Мінімум | Ціль |
|----------|---------|------|
| Processed Samples/s | 80 MS/s | **110+ MS/s** |
| End-to-End Latency | ≤ 50 ms | **≤ 35 ms** |
| GPU Utilization | > 75% | > 90% |
| Dropped Samples | 0 | 0 |
| CPU Usage | < 40% | < 25% |

---

## 6. Додаткові вимоги

- Код повинен бути **модульним**, з чітким API.
- Повна підтримка динамічної зміни параметрів (nfft, hop, threshold тощо) під час роботи.
- Вбудований profiler (час виконання кожного kernel, memory bandwidth, occupancy).
- Можливість збереження spectrogram та detection map у файл для аналізу.
- Детальна документація + коментарі в коді.
- Тестовий стенд з синтетикою + реальними записами ELRS.
