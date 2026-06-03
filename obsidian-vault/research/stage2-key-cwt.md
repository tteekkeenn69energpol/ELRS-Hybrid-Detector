---
tags: [stage-2, knowledge-builder, cwt, sst, bw-estimation, synthesis]
created: 2026-05-29
type: synthesis
stage: 2
status: done
---

# CWT/SST для BW Estimation — Synthesis Note

Конспект ключових фактів про Continuous Wavelet Transform та Synchrosqueezing Transform для оцінки Bandwidth (BW) у Stage 2.

---

## Принцип роботи

**CWT:** `W(a, b) = (1/√a) × ∫ x(t) × ψ*((t-b)/a) dt`

де `a` = scale, `b` = translation.

**Scale → Frequency mapping:** для Morlet wavelet:
`f = f_c / (a × dt)`

де `f_c` — central frequency вейвлету, `dt = 1/samp_rate`.

**Scale → BW mapping для LoRa CSS:**
LoRa chirp rate = BW² / 2^SF
Для фіксованого SF: `a_BW ≈ f_c × 2^SF / (BW × dt)`

---

## Вибір вейвлету

| Вейвлет | Тип | Переваги для ELRS |
|---------|-----|-------------------|
| **Morlet** | Complex, analytic | Відмінна TF локалізація chirps, стандарт для LFM |
| **Morse** | Complex, analytic | Розширює Morlet, кращий контроль decay |
| **Complex Gaussian** | Analytic | Robust до phase noise |
| Biorthogonal | Real | Краще деnoising, але менш precise TF |

**Рекомендація:** Morlet (`'morlet'` в ssqueezepy) — стандарт для chirp-based BW estimation.

---

## SST (Synchrosqueezing Transform)

### Навіщо SST?
CWT alone: energy "розмита" по adjacent scales через finite wavelet support.
SST: reassignment → переміщує коефіцієнти вздовж freq axis до **true instantaneous frequency (IF) ridge**.

### First-order vs Second-order SST

| | First-order SST | Second-order SST (SSST) |
|-|-----------------|------------------------|
| Assumption | Slowly varying IF | Linear FM (chirp rate included) |
| For ELRS | May have bias | Near-perfect energy concentration |
| Library | `ssqueezepy.ssq_cwt` | `ssqueezepy.ssq_cwt(order=2)` |

**Для ELRS:** SSST (second-order) якщо потрібна найвища BW accuracy.

### Чи потрібен SST для нас?
- SST збільшує latency (додаткові обчислення)
- При SNR ≥ -10 dB: першого порядку CWT може бути достатнім
- При SNR < -12 dB: SST критично важливий
- **Рішення:** DSP Research (R2-2) визначає threshold для SST включення

---

## BW Mapping: Scale → kHz

ELRS BW targets: 203 / 406 / 812 / 1625 kHz

### Calibration table (30.72 MS/s, Morlet f_c=1.0)

Для Morlet: `f = f_c / (a × dt)` де `dt = 1/30.72e6`

| BW (kHz) | Відповідний scale `a` |
|----------|----------------------|
| 203 | `f_c × 30.72e6 / 203e3 ≈ 151` |
| 406 | `≈ 75.7` |
| 812 | `≈ 37.8` |
| 1625 | `≈ 18.9` |

*Точні значення залежать від wavelet параметрів — треба калібрувати на synth data (T2-1)*

**Реалізація:**
```python
# Sparse scale set (21 scales замість повного спектра)
target_bws = [203e3, 406e3, 812e3, 1625e3]
target_scales = [f_c * samp_rate / bw for bw in target_bws]

# CWT тільки для target scales
W, scales = cwt(iq_signal, wavelet='morlet', scales=target_scales)
energy = np.abs(W).mean(axis=1)
best_bw_idx = np.argmax(energy)
estimated_bw = target_bws[best_bw_idx]
```

---

## GPU реалізація (CuPy)

```python
import cupy as cp
from ssqueezepy import cwt, ssq_cwt

def cwt_bw_estimation(iq_signal_gpu: cp.ndarray, samp_rate=30.72e6) -> dict:
    target_bws = [203e3, 406e3, 812e3, 1625e3]
    target_scales = [samp_rate / bw for bw in target_bws]  # Morlet f_c=1

    # ssqueezepy підтримує numpy; для GPU — перенести на CPU або CuPy custom
    iq_cpu = cp.asnumpy(iq_signal_gpu) if isinstance(iq_signal_gpu, cp.ndarray) else iq_signal_gpu

    W, scales = cwt(iq_cpu, wavelet='morlet', scales=target_scales, dt=1/samp_rate)
    energy = np.abs(W).mean(axis=1)
    best_idx = np.argmax(energy)

    return {
        'bw': target_bws[best_idx],
        'cwt_energy': float(energy[best_idx]),
        'energy_ratio': float(energy[best_idx] / energy.mean())
    }
```

**Примітка:** ssqueezepy поки що CPU-only. Для GPU: використовувати `cupy.fft` + ручна реалізація CWT через convolution в frequency domain.

---

## Дискретизація Scale (Оптимізація)

**Дослідницьке питання Q21:** чи достатньо 10–20 дискретних масштабів?

**Відповідь:** Для наших цілей (4 discrete BW values) достатньо **4–8 scales** (по 1–2 на BW + interpolation tolerance). Це зменшує latency у порівнянні з повним CWT по всіх scales.

---

## Точність та обмеження

- CWT: добра при SNR ≥ -8 dB
- CWT + SST: до -12 dB
- **Обмеження:** non-standard BW (між 203/406/812/1625) може дати неправильний BW клас

**False BW detection:** найчастіше між сусідніми BW класами (203↔406, 812↔1625).
→ Confidence gate має відловлювати низькоякісні BW estimates.

---

## Посилання

- [[stage2-arch-principles]] — NotebookLM: SST vs CWT, Morlet vs Morse
- [[stage2-dwt-cwt-questions]] — Q2, Q3, Q12, Q21, Q22
- [[stage2-tz-dwt-cwt]] — ТЗ Stage 2 (код cwt_bw_estimation)
- [[03-tz2-dwt-cwt]] — попередній аналіз CWT (KB-2)
- [[stage2-key-dwt]] → попередній крок (SF estimation)
- [[stage2-key-confidence-gate]] → наступний крок (gate + fusion)
- [[ext-ml-rf-36]] — Mutescu 2025: 1D CNN як альтернатива CWT для BW
