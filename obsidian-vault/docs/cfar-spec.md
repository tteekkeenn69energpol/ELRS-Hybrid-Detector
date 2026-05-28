---
tags: [cfar, spec, stage-1, dsp-research]
created: 2026-05-28
status: approved
agent: dsp-research
step: R-3
---

# OS-CFAR Специфікація — Stage 1

> ✅ Заповнено DSP Research агентом. Готово до передачі C++ Dev.
> Джерела: `cfar email.md` (ТЗ), `dataset-cfar.md`, `08-stage1-oscfar-cpp.md`,
> `21-os-cfar-realtime-impl.md`, `17-gpu-stft-cfar-analysis.md`.

## Алгоритм

**2D OS-CFAR** (2-Dimensional Ordered Statistic Constant False Alarm Rate)

Працює на матриці потужності спектрограми **(час × частота)**, отриманій з ланцюга
`IQ → S2V → FFT(shift=True, BlackmanHarris) → |·|² (vlen=fft_size)`.

Для кожної комірки (CUT — Cell Under Test):
1. Виділяється навчальне вікно навколо CUT з виключенням guard-зони.
2. Reference-комірки сортуються за зростанням.
3. Береться `k`-й порядковий елемент → оцінка локального шумового рівня `X(k)`.
4. Адаптивний поріг: `T = α · X(k)`, де `α` обчислюється з заданого `Pfa`.
5. Детекція: `CUT > T  ⇒  detection`.

**Чому OS, а не CA-CFAR:** у середовищі ELRS-FHSS в ISM 915 MHz часто присутні
кілька одночасних передавачів та імпульсні завади (WiFi/BT). CA-CFAR усереднює
викиди → поріг роздувається → `Pd → 0`. OS-CFAR ігнорує до `(N_ref − k)` викидів
і утримує `Pd ≈ 0.58` у тих самих умовах (`dataset-cfar.md` §1).

## Параметри

| Параметр       | Значення           | Обґрунтування |
|----------------|--------------------|---------------|
| `N_guard_f`    | **4**              | Захист по частоті, запобігає self-masking основної лопаті чирпу (`cfar email.md` §2.2, `dataset-cfar.md`: GC 4–6). |
| `N_guard_t`    | **2**              | Захист по часу, преамбула ELRS = 8 up-chirps → достатньо 2 кадрів охорони (`17-gpu-stft-cfar-analysis.md`: guard 4×2). |
| `N_ref_f`      | **16**             | Тренувальні комірки по частоті — стабільна оцінка шуму у ISM-смузі (`17-gpu-stft-cfar-analysis.md`: train 16×8; `cfar email.md`: 12–16). |
| `N_ref_t`      | **8**              | Тренувальні комірки по часу — баланс throughput vs точність (`17-gpu-stft-cfar-analysis.md`). |
| `N_train_total`| **816**            | Reference-комірок у 2D вікні: `(2·16+2·4+1)·(2·8+2·2+1) − (2·4+1)·(2·2+1) = 41·21 − 9·5 = 861 − 45 = 816`. |
| `k`            | **612** (≈0.75·N_train) | 75-й перцентиль → ігнорує до 25% завадних комірок; консенсус усіх 5 джерел (`dataset-cfar.md`: k ≈ ¾·N_T; `17-gpu-stft-cfar-analysis.md`: rank 0.75; `cfar email.md`: 0.75–0.82). |
| `rank_percent` | **0.75**           | Експоновано в API як float для тюнінгу `[0.5, 0.95]`. |
| `α` (scaling)  | обчислюється з Pfa | За формулою Розділу 2 `dataset-cfar.md`: `P_fa = Π_{i=1..k} (N+1−i)/(N+1−i+α)`. Чисельно розв'язується відносно `α` для заданого `Pfa` та `N=N_train_total`. Стартове `α ≈ 17.8` (≈12.5 dB) дає `Pfa ≈ 10⁻²` при `k/N=0.75`. |
| `threshold_dB` (DG)| **12.5 dB** (range 11–14) | Detection Gap — еквівалент `10·log10(α)`. Робочий стартовий поріг з `cfar email.md` §2.2. |
| `min_snr_dB`   | **7 dB**           | Hard floor — навіть якщо CFAR пройшов, SNR нижче 7 дБ відкидається як шум (`cfar email.md` §2.2). |

### Реалізаційна примітка для C++ Dev
- Не сортувати весь масив. Використати `std::nth_element` (O(N) у середньому)
  або partial-sort на reference-комірки. Це ключова оптимізація з
  [[21-os-cfar-realtime-impl.md]] ("rank-only approach").
- Layout матриці: **row-major** (час — рядок, частота — стовпець) для coalesced
  доступу та сумісності з майбутньою CUDA-міграцією (`dataset-cfar.md` §3).
- Edge-handling: для комірок ближчих за `(N_ref + N_guard)` до краю матриці —
  усікати вікно або повертати `no-detection`. Рекомендовано усікання
  (не псує Pfa для внутрішніх комірок).

## Очікувані метрики

| Метрика        | Ціль (Stage 1)               | Допустимий мінімум | Блокує перехід |
|----------------|------------------------------|--------------------|----------------|
| `Pfa`          | ≤ 10⁻² (1%)                  | ≤ 1%               | ✅ ТАК |
| `Pfa` (ціль ТЗ)| ≤ 10⁻⁴ при Pd > 0.92, SNR=−6dB | інформаційно     | ⚠️ Stage 2+ |
| `Pd`           | ≥ 0.92 при SNR = −6 dB (синтетика чистий AWGN) | ≥ 0.58 при наявності завад | ⚠️ Інформаційно (per `cfar email.md` §5) |
| `Throughput`   | ≥ 80 MS/s (CPU C++)          | ≥ 80 MS/s          | ✅ ТАК |
| CFAR-loss (homogeneous) | ≤ +0.53 dB vs CA-CFAR | інформаційно     | ⚠️ Інформаційно |

### Як Pfa зчитується у тестах
Монте-Карло: подати **чистий AWGN** на вхід, прогнати `N_total ≥ 10⁶` комірок,
порахувати `Pfa = N_detections / N_total`. Підтверджується аналітичною формулою
з `dataset-cfar.md` §2.

### Як Pd зчитується у тестах
Згенерувати `N_packets = 10³` синтетичних chirp-преамбул ELRS (8 up-chirps +
2 SYNC + 2.25 down-chirps) при заданому SNR, додати AWGN, прогнати CFAR,
`Pd = N_detected / N_packets`.

## Тестове середовище

- **Синтетичні дані:** AWGN (Rayleigh background) + chirp-сигнал (ELRS-style CSS).
- **SNR sweep:** від −12 dB до +10 dB з кроком 2 dB.
- **Без реальних датасетів на Stage 1.** Реальні IQ-записи з SPECTRAN V6 —
  Stage 2+.
- Спектрограма: `fft_size = 2048`, hop = `fft_size/4` (75% overlap),
  window = Blackman-Harris, `samp_rate = 30.72 MS/s`.

## Інтерфейс для C++ Dev

```cpp
// cfar2d.hpp
#pragma once
#include <cstdint>
#include <vector>

struct Detection {
    int t_idx;        // time index у спектрограмі
    int f_idx;        // freq bin
    float power_db;   // потужність CUT, dB
    float snr_db;     // CUT − noise_estimate, dB
};

struct CFAR2DParams {
    int   N_ref_f      = 16;
    int   N_ref_t      = 8;
    int   N_guard_f    = 4;
    int   N_guard_t    = 2;
    float rank_percent = 0.75f;  // → k = round(rank_percent * N_train_total)
    float threshold_db = 12.5f;  // Detection Gap
    float min_snr_db   = 7.0f;
};

class CFAR2D {
public:
    explicit CFAR2D(const CFAR2DParams& p);

    // input: row-major power matrix (рядок = час, стовпець = частота), float32, лінійна шкала
    // rows = T (час), cols = F (частота)
    std::vector<Detection> process(const float* power, int rows, int cols);

    // Останній виміряний throughput у MS/s (samples-out per second)
    double throughput_ms() const noexcept;

    // Динамічна зміна параметрів без переконструювання
    void set_params(const CFAR2DParams& p);

private:
    CFAR2DParams params_;
    double       last_throughput_ms_ = 0.0;
};
```

### Контракт
- **Thread-safety:** один екземпляр `CFAR2D` — один потік. Багатопотоковість —
  через декілька екземплярів (по тайлах матриці).
- **Алокації:** на гарячому шляху `process()` — без `new`/`malloc`. Усі скретч-
  буфери виділяються у конструкторі або при першому виклику з `rows×cols`.
- **Шкала входу:** лінійна потужність (`|FFT|²`), `float32`. Конверсія в dB —
  всередині класу (для `power_db`/`snr_db`).
- **k обчислюється всередині** з `rank_percent` та фактичного `N_train_total`
  для актуальних `N_ref_*`/`N_guard_*`.

## Залежності та подальші кроки

- C++ Dev (Stage 1) → реалізує `cfar2d.hpp`/`cfar2d.cpp`, інтегрує в OOT-блок
  `gr-elrs_detector` (`08-stage1-oscfar-cpp.md`).
- Test/QA → Монте-Карло Pfa/Pd, ROC, throughput-бенчмарк (`dataset-cfar.md` §4).
- Stage 1.5 (опціонально) → GPU-міграція через CuPy `rank_filter` або
  кастомний CUDA bitonic-sort kernel (`17-gpu-stft-cfar-analysis.md`,
  `dataset-cfar.md` §3).
- Stage 2 → Dechirp + Matched Filter після CFAR (`02-tz1-dechirp-mf`).

## Джерела

1. [[research/cfar email|cfar email.md]] — ТЗ замовника, рекомендовані діапазони параметрів, ROC-цілі.
2. [[research/dataset-cfar|dataset-cfar.md]] — консолідована база знань: формули Pfa/Pd, оптимальні ratios, CUDA-архітектура, методологія тесту.
3. [[research/08-stage1-oscfar-cpp|08-stage1-oscfar-cpp.md]] — структура артефактів C++ OOT-блоку для GNU Radio.
4. [[research/21-os-cfar-realtime-impl|21-os-cfar-realtime-impl.md]] — Bales et al., GTRI/AFRL: rank-only підхід, FPGA/GPU/CPU реалізації, лінійне масштабування.
5. [[research/17-gpu-stft-cfar-analysis|17-gpu-stft-cfar-analysis.md]] — конкретні значення train 16×8, guard 4×2, rank 0.75 для GPU-pipeline.

> Примітка: файл `26-local-oscfar-code-and-tz.md`, на який посилався запит,
> у `/research/` не знайдено на момент R-1 (2026-05-28). Параметри побудовано
> на консенсусі п'яти доступних джерел вище; жодне не суперечить іншому.

## Статус

- [x] Draft
- [x] Підтверджено DSP Research
- [x] Передано C++ Dev
