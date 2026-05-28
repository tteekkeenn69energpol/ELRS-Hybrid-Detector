# DATASET_CFAR — База знань OS-CFAR для ExpressLRS

---
tags: [cfar, dataset, os-cfar, elrs, cuda, gpu, research, stage-1]
created: 2026-05-28
source: Google Drive — папка (CFAR)
type: dataset
stage: 1
status: ready
agent: dsp-research, cpp-dev, test-qa
---

> 📄 Джерело: [DATASET_CFAR на Google Drive](https://docs.google.com/document/d/1ddfS925CoHS0btzCxq8PuLPjfUev5sQxt4QyMA8Y8xE/edit)
> Структура: 5 розділів — Архітектура, Математика, Реалізація CUDA, Тестування, Інтеграція

---

## Розділ 1 — Архітектура та Принципи

### OS-CFAR vs CA-CFAR — ключова відмінність

**CA-CFAR** усереднює тренувальні комірки → одна сильна завада роздуває поріг → маскує ціль → `Pd = 0.0`

**OS-CFAR** сортує комірки → вибирає k-й ранг → ігнорує викиди → `Pd = 0.582` в тих самих умовах

> ⚠️ Для ExpressLRS у ISM-діапазоні OS-CFAR є **математично необхідним**

### Оптимальні параметри вікна

| Параметр                    | Значення             | Призначення                             |
| --------------------------- | -------------------- | --------------------------------------- |
| Guard Cells (GC)            | 4–6                  | Запобігає self-masking коротких пакетів |
| Training Cells (TC) Range   | 10–14                | Стабільна оцінка шуму                   |
| Training Cells (TC) Doppler | 8–28                 | Частотна роздільна здатність            |
| Рекомендований ratio        | 1:2.5 (4 GC : 10 TC) | Базова точка для ELRS                   |
| Rank k                      | ≈ 3/4 × N_train      | Ігнорує до 25% викидів                  |

### Переваги 2D OS-CFAR над 1D

- Накопичення енергії TF-гребенів → +30% виявлених цілей
- Точне визначення меж пакетів (мікросекундна точність)
- Розділення колізій через спектральне перетинання
- Краще керування Pfa в нестаціонарному шумі

---

## Розділ 2 — Алгоритми та Математика

### Аналітична формула Pfa (Rayleigh background)

$$P_{fa} = \prod_{i=1}^{k} \frac{N + 1 - i}{N + 1 - i + \alpha}$$

### Формула Pd (Rayleigh fluctuating target)

$$P_d = \prod_{i=1}^{k} \frac{N + 1 - i}{N + 1 - i + \alpha_D}$$

де `α_D = α / (1 + SNR)`

### Вибір параметра рангу k

| Стратегія | Формула | Застосування |
|-----------|---------|-------------|
| Статичне базове | k ≈ 0.75 × N_T | Загальний robust baseline |
| Захист від завад | k ≤ N_T − J | Середовище з J завадами |
| Динамічний Fuzzy | k_new = k + m (Fuzzy) | Адаптація до clutter edges |
| Variability-Based | Перейти на OS якщо VI > K_VI | Адаптація до локальної нерівномірності |

### Вплив кількості інтегрованих імпульсів N на CFAR-втрати

| N | CA-CFAR Loss | OS-CFAR Loss |
|---|-------------|-------------|
| 1 | ~1.0–1.5 dB | ~2.0–3.0 dB |
| 10 | 0.65 dB | **1.18 dB** |

> Для ELRS: преамбула = 8 up-chirps → оптимально N ≤ 8

---

## Розділ 3 — Реалізація CUDA

### Архітектура ядра

```
Глобальна пам'ять (IQ / спектрограма)
    ↓ Cooperative loading (coalesced, Row-major)
Shared Memory (2D tile + apron/halo)
    ↓ Bitonic Sort (branchless, unrolled)
k-й ранг → поріг T = α × X(k)
    ↓ Порівняння з CUT
Detection List [Time, Freq, Power]
```

### Ключові параметри CUDA

- **Розмір блоку**: 16×16 (256 потоків) — оптимальний баланс
- **Shared Memory apron**: `(Bx + 2×M_r) × (By + 2×M_d) + 1` (padding!)
- **Сортування**: Bitonic Sort — branchless, без warp divergence
- **Складність**: O(N_T × log²N_T) — але без розгалужень

### Оптимізації

- **Kernel Fusion** (STFT + CFAR в одному ядрі) → 2.5x–4x прискорення
- **Row-major** макет для coalesced memory access
- **Padding +1 стовпець** → усуває bank conflicts (Stall MIO)
- **`#pragma unroll`** для циклів сортування
- **Constant Memory** для α (scaling factor)
- **Кілька CUDA streams** → перекриття capture + processing

### Throughput

> ✅ **100 MS/s** досяжний при FPGA binarization + fused CUDA kernels

| Компонент | Стратегія | Результат |
|-----------|-----------|-----------|
| Data Transfer | FPGA Binarization + GPUDirect RDMA | -96% трафіку |
| Spectrogram | Fused Shared-Memory FFT | 4x прискорення |
| Detection | Parallel 2D OS-CFAR + Bitonic Sort | ≥ 100 MS/s |

### Bottlenecks (Nsight Compute)

| Тип | Індикатор | Рішення |
|-----|-----------|---------|
| Bandwidth | Memory SOL > 60%, Long Scoreboard | Shared Memory Tiling |
| Compute | SM SOL > 70%, Exec Dependency | Bitonic Sort + unroll |
| Serialization | MIO Stalls | Padding +1 стовпець |
| Occupancy | Low achieved occupancy | Зменшити register pressure |

---

## Розділ 4 — Тестування та Валідація

### Синтетичні тестові дані для ELRS

```python
# Корисний сигнал — CSS преамбула ELRS
# 8 up-chirps + 2 SYNC + 2.25 down-chirps

# Фоновий шум (вибрати модель):
noise_rayleigh = rayleigh.rvs(size=(256, 256))      # базовий
noise_weibull  = weibull_min.rvs(c=1.5, size=...)  # spiky
noise_kas      = k_distribution(...)                # heavy-tail

# Завади
wifi_packet   = generate_wifi_burst(power_dB=20)
other_elrs    = generate_elrs_packet(sf=SF7)
collision     = overlay(wifi_packet, other_elrs, tau=random_offset)
```

### Ключові метрики тестування

| Метрика | Ціль | Блокує перехід |
|---------|------|---------------|
| Pfa | ≤ 1% | ✅ ТАК |
| Throughput | ≥ 80 MS/s | ✅ ТАК |
| Pd | максимум (базово ~0.582) | ⚠️ Інформаційно |

### Розрахунок Pd в тестах

$$P_d = \frac{N_{detected}}{N_{total}}$$

Де N_total = кількість переданих пакетів (ground truth)

### ROC-крива: OS-CFAR vs CA-CFAR

- При SNR = 20 дБ: OS-CFAR → Pd ≈ 90% при Pfa = 10⁻⁴
- При наявності завад: CA-CFAR → Pd = 0.0, OS-CFAR → Pd ≈ 0.582
- Homogeneous loss OS vs CA: +0.53 dB (прийнятна ціна за robustness)

---

## Розділ 5 — Інтеграція та Масштабування

### Detection List — формат передачі до ML

```python
# Структура: [Max_Detections × 3] tensor
# [0] Time Index   — int32
# [1] Freq Index   — int32
# [2] Power        — float32

# Zero-copy через __cuda_array_interface__
# → ROI patches до CNN/ViT класифікатора
```

### Відображення CFAR → RF частота

```
Δf_bin = f_s / N_FFT
f_offset = (k - N_FFT/2) × Δf_bin
f_RF = f_c + f_offset  (+ поточний стан FHSS LCG)
```

### Бюджет затримки (1000 Гц режим ELRS)

| Етап | Ліміт | Примітка |
|------|-------|---------|
| DMA/RDMA | < 50 мкс | GPUDirect |
| **STFT + CFAR** | **< 200–300 мкс** | Детермінований! |
| ML Classification | < 500 мкс | TensorRT INT8 |
| Jitter Margin | < 100 мкс | Запас |

### Fallback при перевищенні бюджету

1. CA-CFAR → найшвидший, але вразливий до маскування
2. SOCA/GOCA → компроміс швидкість/якість
3. Зменшення вікна N_T → нелінійне прискорення
4. Збільшення stride → лінійне прискорення
5. FPGA binarization → -96% навантаження на GPU

### Портування на FPGA (ZC706)

| GPU (CUDA) | FPGA (ZC706) |
|------------|-------------|
| Bitonic Sort в регістрах | TTL-sorting networks у зсувних регістрах |
| Shared Memory tiling | BRAM delay lines |
| cuFFT | RFNoC FFT blocks |
| CUDA streams | Паралельні апаратні конвеєри |

---

## Швидкий довідник для агентів

### DSP Research → використовувати для специфікації
- Параметри k, N_ref, N_guard з Розділу 1 (таблиця ratios)
- Формули Pfa/Pd з Розділу 2
- Цілі: Pfa ≤ 1%, Throughput ≥ 80 MS/s

### C++ Dev → використовувати для реалізації
- Архітектура ядра з Розділу 3
- Bitonic Sort + Shared Memory pattern
- Block size 16×16, padding +1

### Test/QA → використовувати для тестування
- Синтетичні дані з Розділу 4
- Методологія Монте-Карло для Pd
- ROC curves + benchmark throughput

### Docs → посилання
- [[cfar-spec]] ← заповнить DSP Research
- [[agents/dsp-research]]
- [[agents/cpp-dev]]
- [[agents/test-qa]]
