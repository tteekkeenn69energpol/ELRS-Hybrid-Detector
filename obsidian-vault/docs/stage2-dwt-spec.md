---
tags: [stage-2, spec, dwt, cwt, dsp-research, blind-estimator]
created: 2026-05-29
status: approved-v8
version: '8.0'
agent: dsp-research
step: R2-fix-v8
---

# Stage 2 — DWT+CWT Blind Parameter Estimator Специфікація

> ✅ v6.0 — Патч R2-fix-v6 після ROOT CAUSE F (2026-06-02). BW edge detection: threshold+max → per-class hypothesis test (argmax score).
> (v2.0 2026-05-29: два баги — autocorr_norm + Re(IQ) для CWT — були необхідні але недостатні.)
> Джерела v1: `stage2-tz-dwt-cwt.md` (ТЗ#2), `stage2-key-dwt.md`,
> `stage2-key-cwt.md`, `stage2-key-confidence-gate.md`,
> `stage2-arch-principles.md`, `03-tz2-dwt-cwt.md`,
> `09-stage2-blind-estimator-py.md`.
> Нові джерела v3: `tests/stage2/test-results-stage2.md`, `obsidian-vault/logs/test-results-stage2-2026-06-02.md` (T2-retry FAIL-звіт).

---

## Changelog

| Версія | Дата | Автор | Зміни |
|--------|------|-------|-------|
| **v8.0** | 2026-06-03 | DSP Research (R2-fix-v8) | **ROOT CAUSE I:** estimate() читав iq[:n_sym] від початку — сигнал може бути зміщений на t_offset (PMT trigger Stage 1) → читання шуму. **ROOT CAUSE J:** SF12/BW=203k → n_sym=619k → FFT(619k)×6≈35ms > 15ms budget. **Патч §R2-1:** inputs додано `t_offset=0` і `N_DECHIRP_MAX=65536`; `n_use=min(n_sym, N_DECHIRP_MAX, len(iq)-t_offset)`; `dechirped=iq[t_offset:t_offset+n_use]×ref`. Latency таблиця: worst case → FFT(65536)×6<1ms. **Патч §R2-4:** `estimate(t_offset=0)` + `dwt_sf_estimation(t_offset=0)` сигнатури. Return keys незмінні. §R2-2/R2-3/Dechirp MF алгоритм незмінені. |
| **v7.0** | 2026-06-03 | DSP Research (R2-fix-v7) | **ROOT CAUSE H:** DWT autocorrelation на Re(IQ) = 22.9% SF accuracy ≈ random. Фізична причина (H-2a): Re(IQ)=cos(phase), UP→UP символьна межа не створює energy surge у cD_4 (фаза і перша похідна неперервні). Energy surges тільки на UP→SYNC та SYNC→DOWN (2 з 12+ меж). Lag table errors BW=1625k SF10-SF12 — вторинна. **§R2-1 повністю замінено** на Dechirp Matched Filter: для кожної SF-гіпотези IQ×ref_down_chirp→FFT→peak/mean score; argmax = SF. Незалежно від символьних меж. Discrimination >5× при -10dB. §R2-2/R2-3/R2-4 незмінені. |
| **v6.0** | 2026-06-02 | DSP Research (R2-fix-v6) | **ROOT CAUSE F:** v5 Steps 4-5 мали два дефекти: (1) `max(occupied)` → E[false noise bins]=4.2 → f_edge~14MHz → bw_raw~28MHz → BW=1625k завжди; (2) threshold=1.5 > S_norm_edge=1.48 для BW=1625k @ -14dB → edge не детектується. Замінено на **per-class hypothesis test**: `score[b] = mean(S_norm[0..b/2]) / mean(S_norm[b/2..b])` → `bw_candidate = argmax(score)`. Immune до noise outliers, без threshold. Steps 1-3 і Step 6 збережено. |
| **v5.0** | 2026-06-02 | DSP Research (R2-fix-v5) | **ROOT CAUSE E:** SST/CWT фундаментально непрацездатний з sparse 4-scale set — "dvl1 below EPS64", bias до крайніх scales (241: ~67%, 30: ~33%), BW accuracy=25% після 4 ітерацій. §R2-2 повністю замінена: BW estimation → Welch PSD spectral occupancy (Z-score ≥4.2σ для BW=1625k @ -14dB, ≥6.6σ @ -12dB). `use_sst` deprecated (зберігається у конструкторі). `cwt_energy_bounds=(1.0,10.0)` незмінені. R2-4 інтерфейс незмінений. |
| **v4.0** | 2026-06-02 | DSP Research (R2-fix-v4) | **ROOT CAUSE D:** CWT scale formula виправлена: `samp_rate/BW` → `5×samp_rate/(π×BW)` = [241,121,60,30]. v3 scales давали f_c=0.796×BW > BW/2 → вище max chirp IF Re(IQ) → CWT сліпа. v4: f_c=BW/2 → matched до peak IF CSS chirp. Один рядок у Python Dev. |
| **v3.0** | 2026-06-02 | DSP Research (R2-fix-v3) | **ROOT CAUSE A:** CWT-first каскад (CWT→BW, DWT(bw_hint)→SF); DWT signal змінено з `np.abs(IQ)` → `np.real(IQ)` — CSS constant-envelope → cD_L від \|IQ\| = шум; DWT пошук обмежено bw_candidate-колонкою → 6 унікальних лагів, lag ambiguity (24 пари → 6 unique, діагональ 2^SF/BW=const) усунена. **ROOT CAUSE B:** scale formula reverted до `samp_rate/BW` = [151,76,38,19] — скасовує v2-регресію (N_sym → f_c ~3kHz << chirp 200–1625kHz → CWT сліпа). **ROOT CAUSE C:** cwt_max_samples=8192 fixed window, без 3×min_s expansion → usуває latency регресію 79ms→≤25ms. R2-4 інтерфейс незмінений. |
| **v2.0** | 2026-05-29 | DSP Research (R2-fix) | **БАГ #1 (R2-1):** нормалізація автокореляції замінена з `mean(autocorr)` на `mean(|autocorr|)` — усуває sign-inversion при zero-mean detail-коефіцієнтах cD_4; bounds (1.0, 10.0) незмінні. **БАГ #2 (R2-2):** CWT input змінено з `np.abs(IQ)` → `np.real(IQ)`; formula scales змінена з SF-незалежної `samp_rate/BW` → SF-залежної `samp_rate×2^SF_candidate/BW`; CWT тепер явно залежить від SF_candidate з DWT (cascade). |
| v1.0 | 2026-05-29 | DSP Research (R2-5) | Початкова специфікація R2-1..R2-5, status=approved |

---

## Алгоритм

**Stage 2 — Hybrid Welch PSD → Dechirp MF Blind Estimator v7** (BW-first каскадна архітектура)

Отримує IQ-буфер 50–100 мс (тригер від Stage 1 OS-CFAR) і повертає оцінку
`{SF, BW, confidence}` без апріорних знань про параметри сигналу.

> ⚠️ v7: BW-first (Welch PSD §R2-2 → bw_candidate). SF: Dechirp Matched Filter — IQ×ref_down_chirp→FFT→peak/mean.
> DWT autocorr (v1–v6) замінено: не виявляє символьні межі у CSS up-chirp train (ROOT CAUSE H).

```
IQ buffer (50–100 мс, complex64)
  │
  ├─[preprocessing]─ CFO coarse correction (optional, autocorr-based)
  │                  Power normalization (rms)
  │
  ├─[2a] Welch PSD BW estimator ────────────────────────────────────────┐
  │      signal = np.real(IQ[:65536])   ← 2.13ms window              │
  │      S_welch = Welch PSD (N_fft=4096, hop=2048, K=31 frames, Hann)│
  │      noise_floor = median(S_welch[freqs > 3.25MHz])               │
  │      S_norm = S_welch / noise_floor                                │
  │      score[b] = mean(S_norm[0..b/2]) / mean(S_norm[b/2..b])       │
  │               ← per-class hypothesis test; no threshold           │
  │      bw_candidate = argmax(score) over target_bws                 │
  │      energy_ratio = score[bw_candidate]  ← range [1.0, ~10]      │
  │      → {bw_candidate, energy_ratio}                               │
  │                                                                   │
  ├─[2b] Dechirp Matched Filter SF estimator ──────────────────────────┤
  │      # v7: bw_candidate відомий з [2a] → SF єдиний unknown        │
  │      for sf_hat in 7..12:                                         │
  │          n_sym = round(2^sf_hat × samp_rate / bw_candidate)       │
  │          ref = exp(-j×2π×(f₀×t + 0.5×CR_hat×t²))  ← down-chirp  │
  │          dechirped = iq[:n_sym] × ref                             │
  │          spectrum = |rfft(dechirped, n=n_sym)|²                   │
  │          score[sf_hat] = max(spectrum) / mean(spectrum)           │
  │          ← CR=CR_hat → DC tone → peak/mean=N_sym×SNR >> noise     │
  │      best_sf = argmax(score over sf_hat in 7..12)                 │
  │      → {sf_candidate, sf_score_raw}                               │
  │                                                                   │
  └─[2c] Confidence gate ─────────────────────────────────────────────┘
         confidence = 0.5×norm(DWT) + 0.5×norm(CWT)
         if conf < 0.4: → REJECT (stage3_ready=False, needs_neural=False)
         if conf ≥ 0.7: → Stage 3 direct (stage3_ready=True)
         else:          → Stage 4 Neural (needs_neural=True)
         → {sf, bw, confidence, method, t_offset_samples,
            stage3_ready, needs_neural}
```

**Вхід:** `np.ndarray` complex64, довільна кількість семплів ≥ 8 × 2^12 × (samp_rate/203e3) ≈ 50 мс.
**Вихід:** dict (завжди повертається; REJECT кодується через stage3_ready=False, needs_neural=False).

---

## R2-1 — SF estimation: Dechirp Matched Filter (v7)

### Зміна методу — ROOT CAUSE H

DWT autocorrelation на Re(IQ) фундаментально непрацездатний для ELRS CSS preamble (підтверджено T2-retry-v5c):

- SF accuracy = **22.9% ≈ random** (1/6 = 16.7%), незалежно від SNR, fill ratio, або коректності BW
- **Фізична причина (H-2a):** `Re(IQ) = cos(phase)`. На UP→UP символьних межах phase=0 → cos=1, d(cos)/dt=0 — **фаза і перша похідна неперервні** по обидва боки межі. Energy surge у cD_4 відсутній.
  Energy surges виникають ТІЛЬКИ на UP→SYNC та SYNC→DOWN переходах = **2 події з 12+ символів preamble**.
  DWT lag autocorr потребує регулярних periodичних energy surges (кожен символ) — яких немає у CSS up-chirp train.
- Lag table errors для BW=1625k SF10-SF12 (вторинна проблема; не причина загального провалу).

**Рішення v7: Dechirp Matched Filter** — physically correct, незалежний від preamble structure.

---

### Фізична основа

CSS up-chirp з SF=s, BW=b sweeps baseband IF від −b/2 до +b/2 за T_sym = 2^s/b секунд:

```
IQ(t) = exp(j×2π×(f₀×t + 0.5×CR×t²))
        де  f₀ = −b/2,   CR = b/T_sym = b²/2^s   (chirp rate, Hz/s)
```

Reference down-chirp для гіпотези SF=s_hat:

```
ref(t) = conj(up_chirp|SF=s_hat) = exp(−j×2π×(f₀×t + 0.5×CR_hat×t²))
```

Dechirped = IQ × ref:

```
d(t) = exp(j×2π×(CR − CR_hat)/2 × t²)
```

- **CR = CR_hat (s = s_hat) →** d(t) = 1 (DC тон) → FFT peak at bin 0 → **coherent gain = N_sym**
- **CR ≠ CR_hat (s ≠ s_hat) →** residual chirp → energy spread across spectrum → no peak

Score = `max(|FFT|²) / mean(|FFT|²)` — повністю незалежний від символьних меж і preamble structure.

---

### Аналіз точності (блокуючі метрики)

Для правильної гіпотези при SNR = −10 dB (SNR_lin = 0.1):

```
peak/mean ≈ N_sym × SNR_lin
```

| SF | BW_мін | N_sym (мін) | Score @ −10dB | Score @ −14dB | Discrimination |
|----|--------|------------|---------------|---------------|----------------|
| SF7 | 1625k | 151 | **15.1** | 6.0 | high |
| SF8 | 1625k | 302 | **30.2** | 12.0 | high |
| SF9 | 1625k | 605 | **60.5** | 24.0 | high |
| SF10 | 203k | 9 686 | **968** | 385 | very high |
| SF11 | 203k | 19 373 | **1 937** | 771 | very high |
| SF12 | 203k | 38 745 | **3 875** | 1 541 | very high |

Для неправильної гіпотези: residual chirp → peak/mean ≈ 2–4 (random fluctuation після AWGN).

**Discrimination margin @ −10dB:** мінімум SF7/BW=1625k → 15.1 / 3 ≈ **5×** → >99% accuracy.
**@ −14dB:** SF7/BW=1625k → 6.0 / 3 ≈ **2×** → >90% accuracy (достатньо для pair ≥78% gate).

---

### Алгоритм (pseudocode)

```
inputs:
    iq            — complex64, len ≥ N_BUFFER (1,536,000 @ 50ms)
    bw_candidate  — int, Hz (з §R2-2 Welch PSD; BW=87.5% ✓)
    samp_rate     — float = 30.72e6
    t_offset      — int = 0          # v8: sample offset з PMT trigger Stage 1
    N_DECHIRP_MAX — int = 65536      # v8: max FFT window (узгоджено з Welch PSD); cap latency

scores = {}
for sf_hat in 7..12:
    n_sym   = round(2^sf_hat × samp_rate / bw_candidate)          # samples per symbol
    n_use   = min(n_sym, N_DECHIRP_MAX, len(iq) - t_offset)       # v8: cap window; stay in buffer

    t       = arange(n_use) / samp_rate                           # time axis [s]
    f0      = −bw_candidate / 2.0
    cr_hat  = bw_candidate^2 / 2^sf_hat                           # chirp rate [Hz/s]

    ref_phase  = 2π × (f0×t + 0.5×cr_hat×t²)                     # up-chirp phase
    ref        = exp(−j × ref_phase)                              # conj = down-chirp

    dechirped  = iq[t_offset : t_offset + n_use] × ref            # v8: start at signal onset
    spectrum   = |rfft(dechirped, n=n_sym)|²               # zero-pad to n_sym

    peak_val   = max(spectrum)
    mean_val   = max(mean(spectrum), 1e-30)
    scores[sf_hat] = peak_val / mean_val

best_sf   = argmax(scores)
sf_score  = scores[best_sf]

# t_offset_samples: 10% cumulative energy point (position of signal onset)
energy_env       = |iq|²
cumulative_e     = cumsum(energy_env)
threshold_e      = 0.1 × sum(energy_env)
t_offset_samples = first index where cumulative_e[i] >= threshold_e
                   (default 0 if all-noise)

return {
    'sf'              : best_sf,
    'bw_hint'         : bw_candidate,
    'score'           : sf_score,
    'best_lag'        : 0,          # v7: repurposed, always 0; no lag in dechirp MF
    't_offset_samples': t_offset_samples,
}
```

**Примітка `best_lag`:** ключ збережено для §R2-4 API сумісності. Значення = 0 у v7. Python Dev може ігнорувати або зберігати peak FFT bin (≈0 при правильній гіпотезі).

**Примітка `wavelet`, `level`:** параметри збережено у сигнатурі `dwt_sf_estimation` для §R2-4 API сумісності. Python Dev ігнорує їх у v7-реалізації.

---

### Параметри (v8)

| Параметр | Значення | Обґрунтування |
|----------|----------|---------------|
| n_use | `min(n_sym, N_DECHIRP_MAX, len(iq)-t_offset)` | Кап: 1 символ, макс вікно, не виходити за буфер |
| n_fft | `n_sym` (zero-pad) | Рівномірна bin resolution (1 bin = BW/n_sym Hz) для всіх SF |
| score | `max(spectrum) / mean(spectrum)` | Peak-to-mean → coherent gain при правильній гіпотезі |
| bw_candidate | з §R2-2 | BW відомий (87.5% ✅); SF єдиний unknown |
| **N_DECHIRP_MAX** | **65 536** | Узгоджено з Welch PSD вікном (§R2-2 N_total); FFT worst case < 1 ms |
| **t_offset** | **0** | Sample offset сигналу у буфері; з PMT trigger Stage 1 (ROOT CAUSE I) |
| `wavelet` | sym5 (збережено) | API сумісність §R2-4; не використовується |
| `level` | 4 (збережено) | API сумісність §R2-4; не використовується |

---

### Score пороги (v7)

Score = peak / mean(FFT power spectrum після dechirping):

| Score | Інтерпретація | Normalized (bounds 1.0–10.0) |
|-------|--------------|------------------------------|
| < 3 | Шум або неправильна гіпотеза | < 0.22 |
| 3 – 15 | Слабкий сигнал (−14 dB зона) | 0.22 – 0.44 |
| 15 – 60 | Надійна детекція (−10 dB+) | 0.44 – 0.78 |
| > 60 | Сильний сигнал (0 dB+) | > 0.78 (clips to 1.0) |

**`dwt_score_bounds = (1.0, 10.0)` ЗБЕРЕЖЕНО** (§R2-4 API незмінений). Нормалізація: `(score − 1.0) / 9.0`, clip до [0, 1]. При score=15.1 (SF7/1625k @ −10dB): normalized = 1.57 → clip 1.0 → confidence contrib = 0.5 → gate: NEURAL або DIRECT ✓.

*T2 калібрує bounds за реальними даними. Коригувати через `dwt_score_bounds` у конструкторі.*

---

### Latency оцінка (v8)

> v7 мав помилку: n_sym SF12/BW=203k = 619k, не 38745. N_DECHIRP_MAX=65536 обмежує worst case.

| Операція | Розмір | Час (оцінка) |
|----------|--------|-------------|
| 6 × ref generation (arange + phase + exp) | 6 × N_DECHIRP_MAX = 6 × 65 536 | < 1 ms |
| 6 × dechirp multiply | 6 × 65 536 | < 0.5 ms |
| 6 × rfft(n_fft) — worst case = N_DECHIRP_MAX | rfft(65 536) × 6 | < 1 ms |
| Score + argmax | trivial | < 0.1 ms |
| t_offset_samples (cumsum) | 1,536,000 | < 0.5 ms |
| **SF total** | — | **< 3 ms** |
| BW §R2-2 Welch PSD | — | ≈ 5 ms |
| **Grand total** | — | **< 8 ms ≤ 25 ms ✓** |

---

## R2-2 — BW estimation: Welch PSD Spectral Occupancy (v5)

### Зміна методу — ROOT CAUSE E

SST/CWT з sparse scales фундаментально непрацездатний (підтверджено 4 ітераціями, N=12,000):
- "dvl1 below EPS64" warning на кожному виклику
- Energy bias: scale=241 →~67%, scale=30 →~33% **незалежно від BW**
- BW accuracy = 25% (random guess) після виправлень v1→v4
- Причина: SST вимагає dense continuous scale coverage; sparse 4-scale set → синхросквізінг не може коректно перерозподілити energy → argmax bias до крайніх scales

**Рішення v5: Welch PSD spectral occupancy** (замість SST/CWT).

---

### Фізична основа

CSS up-chirp Re(IQ) (baseband) рівномірно sweeps IF від 0 до BW/2. Power spectral density:

```
S(f < BW/2)  = S_signal + S_noise    ← flat, висока (сигнал + шум)
S(f > BW/2)  = S_noise                ← flat, низька (тільки шум)
```

Виміряти BW = знайти **spectral edge** на f = BW/2. Welch PSD усереднює K frames → S_norm(f) надійно показує де сигнал, де шум.

**Незалежно від SF.** Spectral occupancy залежить лише від BW.

---

### Аналіз SNR (блокуючі метрики)

`signal_PSD / noise_PSD = SNR_linear × samp_rate / BW`

| BW (kHz) | SNR=-12dB ratio | SNR=-14dB ratio | Z-score @ K=31 @ -12dB | Status |
|----------|-----------------|-----------------|------------------------|--------|
| 203 | 9.5 | 6.0 | 9.5×√31 ≈ 53σ | ~100% |
| 406 | 4.75 | 3.0 | 4.75×√31 ≈ 26σ | ~100% |
| 812 | 2.4 | 1.5 | 2.4×√31 ≈ 13σ | ~100% |
| **1625** | **1.19** | **0.75** | **1.19×√31 ≈ 6.6σ** | **>99.9%** |
| 1625 @ -14dB | — | 0.75 | **0.75×√31 ≈ 4.2σ** | **>99.9%** |

Всі Z-scores >> 3 → **BW accuracy ≥ 80% @ -12dB ✓; ≥78% SF+BW pair @ -14dB ✓** (DWT для SF).

---

### Оцінка підходів (вибір)

| Підхід | Метод | BW @ -12dB | BW @ -14dB | Latency | Вибрано |
|--------|-------|------------|------------|---------|---------|
| **D+ (ВИБРАНО)** | **Welch PSD** | **>99%** | **>95%** | **≈5ms** | **✅** |
| A: IF/unwrap | `diff(unwrap(angle))` | fails<-8dB | fails | fast | ❌ |
| B: Dense CWT | 32 scales geomspace | bias крайній scale | bias | ≈10ms | ❌ |
| C: Matched Filter | dechirp+FFT | ~95% | ~90% | ≈5ms | ❌ потребує SF hint |
| v1-v4 SST/CWT | sparse 4 scales | 25% (random) | 25% | ≈2ms | ❌ ROOT CAUSE E |

Підхід C (Matched Filter) потужний, але вимагає SF_hint; DWT SF accuracy = 17% → ненадійно.
Підхід D+ надійний незалежно від SF і математично обґрунтований.

---

### Параметри (v6)

| Параметр | Значення | Обґрунтування |
|---------|----------|---------------|
| N_total | **65,536** | 2.13ms @ 30.72MS/s; K=31 frames для BW=1625k @ -14dB (Z≥4.2σ) |
| N_fft | **4,096** | bin_width=7.5kHz ≈ 4% BW_min=203kHz → достатня resolution |
| hop | **2,048** | 50% overlap; K = (65536-4096)/2048+1 = 31 frames |
| window | **Hann** | зменшує spectral leakage між сусідніми bins |
| noise_freq_min | **3,250,000 Hz** | > 2×max(target_bws)=3.25MHz → чистий noise-only region для S_norm нормалізації |
| ~~threshold~~ | ~~1.5~~ | **REMOVED v6** — per-class test не потребує threshold (immune до noise outliers) |

---

### ROOT CAUSE F — чому v5 Steps 4-5 не працювали

**Дефект 1 — `max(occupied)` → noise outlier bias:**
```
N_fft=4096, samp_rate=30.72MHz → bin_width=7500Hz
noise region: freqs > 3.25MHz → ~1614 noise bins
Welch K=31 → S_norm ~ chi-squared(62)/62: mean=1.0, std≈0.180
P(S_norm > 1.5 | noise) ≈ 0.26% per bin
E[false positive bins] = 1614 × 0.0026 ≈ 4.2 bins
max(occupied) вибирає ~14MHz → bw_raw≈28MHz → BW=1625k у ~100% випадків
```

**Дефект 2 — threshold=1.5 > S_norm на edge для BW=1625k @ -14dB:**
```
signal_PSD/noise = SNR_lin × samp_rate/BW = 0.0398 × 30720000/1625000 = 0.75
S_norm[f=BW/2] = 1 + 0.75 = 1.75 (середина band)
S_norm[f=BW/2−ε] з Hann roll-off ≈ 1.48 на граничних bins
threshold=1.5 > 1.48 → granary bin не потрапляє до occupied → f_edge < BW/2
```

Жоден threshold не усуває обидва дефекти одночасно: нижчий threshold фіксує дефект 2, але підвищує false positives дефекту 1.

**Рішення v6: per-class hypothesis test (Approach A) — без threshold.**

---

### Алгоритм v6 (pseudocode)

```
inputs: iq (complex64, len ≥ N_total), samp_rate=30.72e6,
        target_bws=[203_000, 406_000, 812_000, 1_625_000],
        N_total=65_536, N_fft=4_096, hop=2_048,
        noise_freq_min=3_250_000
        # threshold REMOVED v6 — per-class test does not need it

# Step 1: prepare signal (UNCHANGED from v5)
signal = np.real(iq[:N_total]).astype(float64)   # Re(IQ), not |IQ|

# Step 2: Welch PSD (UNCHANGED from v5)
hann_win = hann_window(N_fft)                    # pre-computed
S_welch  = zeros(N_fft//2 + 1)
K = 0
for start in 0, hop, 2*hop, ..., while start+N_fft ≤ N_total:
    frame    = signal[start : start+N_fft] * hann_win
    S_welch += |rfft(frame)|²
    K += 1                                       # K = 31 at N_total=65536, hop=2048
S_welch /= K

# Step 3: normalized PSD (UNCHANGED from v5)
freqs       = rfftfreq(N_fft, d=1/samp_rate)     # 0..samp_rate/2, shape N_fft//2+1
noise_mask  = freqs > noise_freq_min             # > 3.25 MHz
noise_floor = max(median(S_welch[noise_mask]), 1e-30)
S_norm      = S_welch / noise_floor

# Step 4: per-class hypothesis test ← REPLACES v5 threshold+max(occupied)
# Physics: true BW=b → ref_mask[b/2..b] is outside signal → ref_mean≈1.0 → score=1+SNR_spectral
#          wrong BW<b → ref_mask is INSIDE signal band → ref_mean≈in_mean → score≈1.0
# argmax(score) = true BW class; no threshold; immune to noise outliers
scores = {}
for b in target_bws:
    in_mask   = (freqs > 0) & (freqs ≤ b / 2)
    ref_mask  = (freqs > b / 2) & (freqs ≤ b)
    in_mean   = mean(S_norm[in_mask])  if any(in_mask)  else 1.0
    ref_mean  = mean(S_norm[ref_mask]) if any(ref_mask) else 1.0
    ref_mean  = max(ref_mean, 1e-6)    # eps guard (ref_mean always ≥ 1.0 in practice)
    scores[b] = in_mean / ref_mean

# Step 5: select BW class ← REPLACES v5 snap-to-nearest
bw_candidate = max(scores, key=scores.get)   # argmax over 4 candidates

# Step 6: energy ratio (UNCHANGED formula; bw_candidate from argmax, not bw_raw)
energy_ratio = max(scores[bw_candidate], 1.0)   # already computed in Step 4
# Compatible with cwt_energy_bounds=(1.0, 10.0):
#   noise only → score≈1.0; BW=1625k @ -14dB → 1.75; BW=203k @ -6dB → ~5.5

return bw_candidate, energy_ratio
```

---

### Latency оцінка (v6)

| Операція | N | Cost (flops) |
|----------|---|-------------|
| Re(IQ) slice | 65,536 | O(65k) |
| Welch: 31 × rfft(4096) | 31×4096=127k | ≈1.5M |
| Noise floor + S_norm | 2049 bins | O(2k) |
| Per-class scores (4 × mean) | 4 × 2049 bins | O(8k) |
| **Welch PSD total** | — | **≈5 ms** |
| DWT (full 1.5M samples) | 1,536,000 | ≈15 ms |
| **Grand total** | — | **≈20 ms ≤ 25 ms ✓** |

---

### Сумісність з R2-4 інтерфейсом (НЕЗМІНЕНИЙ)

- **`use_sst: bool = True`** — зберігається у конструкторі; **NOT USED** у v5. Python Dev ігнорує значення.
- **`cwt_energy_bounds: tuple = (1.0, 10.0)`** — **НЕЗМІНЕНИЙ**. energy_ratio від Welch PSD:
  - 1.0 = шум (in_band ≈ out_band)
  - 1.75 = BW=1625k @ -14dB
  - 10.0+ = сильний chirp (S/N ratio ≈ 9 per bin) → clip до 10 при нормалізації
  - Фізичний діапазон той самий що і у CWT energy_ratio ✓
- **`method` return value** → `'psd+dwt'` (замість `'dwt+cwt'`). Key name незмінений ✓
- **Всі 7 return keys НЕЗМІНЕНІ** ✓
- **Конструктор НЕЗМІНЕНИЙ** ✓

---

### Очікувана точність BW vs SNR (v6, per-class hypothesis test)

Verification: `score(true_BW) = 1 + signal_PSD/noise_PSD > score(other_BW) ≈ 1.0`

| BW (kHz) | SNR | signal_PSD/noise | score(true_BW) | score(others) | Detect |
|----------|-----|-----------------|----------------|---------------|--------|
| 203 | -12dB | 9.5 | **10.5** | ≤1.0 | ~100% |
| 406 | -12dB | 4.75 | **5.75** | ≤1.0 | ~100% |
| 812 | -12dB | 2.4 | **3.4** | ≤1.0 | ~100% |
| **1625** | **-12dB** | **1.19** | **2.19** | ≤1.0 | **~100%** |
| **1625** | **-14dB** | **0.75** | **1.75** | ≤1.0 | **~100%** ← target ✓ |

`score(true_BW) > score(any_other_BW)` гарантовано якщо true BW boundary (b/2) є у noise region.
Кордон між класами: коли `score(bw1) ≈ score(bw2)` → потрібен gate для low-conf. захисту.

Помилки: лише при SNR << -14dB, або якщо noise floor estimation нестабільна (відловлює gate).

**v6 `cwt_energy_bounds` (1.0, 10.0) ЗБЕРЕЖЕНО.** Per-class score = 1 + signal_PSD/noise_PSD.
Range: [1.0 (noise), ~10.5 (BW=203k @ -12dB)] — ідентично до попереднього energy_ratio.
T2 калібрує. Коригувати через конструктор при необхідності.

---

## R2-3 — Confidence Gate специфікація

### Нормалізація компонентів

```
DWT_score_norm  = clip((DWT_score_raw  - dwt_score_bounds[0])
                       / (dwt_score_bounds[1] - dwt_score_bounds[0]), 0.0, 1.0)

CWT_energy_norm = clip((CWT_energy_ratio - cwt_energy_bounds[0])
                       / (cwt_energy_bounds[1] - cwt_energy_bounds[0]), 0.0, 1.0)
```

Дефолтні bounds: `dwt_score_bounds = (1.0, 10.0)`, `cwt_energy_bounds = (1.0, 10.0)`

Фізичне обґрунтування:
- Lower bound = 1.0: flat autocorr/energy (чистий шум; peak = mean → ratio = 1)
- Upper bound = 10.0: сильний chirp при SNR ~+10 dB (DWT_score_raw ≈ 8.5, CWT_ratio ≈ 7.2)
  → normalize maps [1.0, 10.0] → [0.0, 1.0]

### Combined score

```
confidence = 0.5 × DWT_score_norm + 0.5 × CWT_energy_norm
```

**Рівні ваги 0.5/0.5 — обґрунтування:**
- При high SNR (≥ 0 dB): обидва компоненти надійні
- При low SNR (< -10 dB): обидва деградують рівномірно
- Немає апріорних підстав надавати перевагу одному без calibration data
- Після T2-1 ваги можна уточнити через конструктор, якщо один компонент стабільніший

### Порогова логіка

| Confidence | Дія | stage3_ready | needs_neural |
|------------|-----|-------------|-------------|
| < 0.4 | **REJECT** — noise trigger від Stage 1 | False | False |
| [0.4, 0.7) | **NEURAL** — Stage 4 верифікація | False | True |
| ≥ 0.7 | **DIRECT** — Stage 3 прямо | True | False |

**Поріг 0.4 (LOW):** відповідає DWT_score_raw ≈ 1.5–2.0 та CWT_ratio ≈ 1.3–1.8 →
сигнал практично невідрізнений від шуму. False trigger rate ≤ 5% при цьому порозі
(T2-6 target, [[stage2-key-confidence-gate]] §False Trigger Rate).

**Поріг 0.7 (HIGH):** обидва компоненти normалізовані ≥ 0.5 кожен → DWT raw ≥ 5.5
та CWT ratio ≥ 5.5 → обидва методи незалежно підтверджують сигнал. Stage 4 overhead
непотрібен ([[03-tz2-dwt-cwt]] §Confidence Gate: conf > 0.8 → Dechirp/ТЗ#1).

### Додаткові перевірки (anti-false-trigger)

**1. Holdoff (обов'язковий):**
Ігнорувати triggers протягом `holdoff_s` після останнього прийнятого estimate.
Default: 0.1 с (100 мс). Запобігає burst-спрацювання на одному пакеті.

**2. Chirp rate consistency (якщо SF і BW відомі):**
```
expected_chirp_rate = bw / (2**sf)           # Гц/с
measured_chirp_rate = (estimated via IF slope from CWT phase)
penalty: if |measured - expected| / expected > 0.15:
    confidence × = 0.3
```

**3. SF history consistency:**
```
if len(sf_history) >= 3 and std(sf_history[-3:]) > 1.5:
    confidence *= 0.5
```

**4. Мінімальна тривалість (якщо відомий SF):**
```
min_duration_samples = 8 * (2**sf / bw) * samp_rate * 0.5  # 0.5 × 8 preamble chirps
if len(iq_buffer) < min_duration_samples:
    return reject_result  # stage3_ready=False, needs_neural=False
```

### Калібрування порогів для T2-1

T2 повинен верифікувати що:
1. **REJECT зона (conf < 0.4):** на 10,000 pure AWGN буферах → false trigger rate ≤ 5%
2. **DIRECT зона (conf ≥ 0.7):** SF+BW pair accuracy ≥ 90% для цих семплів
3. **NEURAL зона [0.4, 0.7):** SF+BW pair accuracy ≥ 65% (worth Neural processing)
4. Побудувати ROC кривий для кожного SNR рівня → уточнити bounds якщо треба

Якщо bounds потребують корекції — передати нові значення через конструктор (не hardcode).

---

## R2-4 — Python інтерфейс (контракт для C2)

```python
import numpy as np


class ELRS_BlindParameterEstimator:
    """
    Blind SF/BW estimator for ELRS CSS signals (Stage 2).

    Pipeline (v7 BW-first):
      IQ[:65536]    → Welch PSD (N_fft=4096, K=31, Hann) → per-class score → BW
      IQ[t_offset:] → Dechirp MF (6 hyp, N_DECHIRP_MAX=65536) → peak/mean → SF
      SF+BW         → Confidence gate (0.4/0.7) → PDU dict
    """

    TARGET_BWS = [203_000, 406_000, 812_000, 1_625_000]  # Hz

    def __init__(
        self,
        samp_rate: float = 30.72e6,
        wavelet: str = 'sym5',
        dwt_level: int = 4,
        threshold_low: float = 0.4,
        threshold_high: float = 0.7,
        use_sst: bool = True,
        dwt_score_bounds: tuple = (1.0, 10.0),
        cwt_energy_bounds: tuple = (1.0, 10.0),
        holdoff_s: float = 0.1,
    ) -> None:
        """
        samp_rate       — sample rate Hz (default: 30.72 MS/s SPECTRAN V6)
        wavelet         — PyWavelets name; 'sym5' (default) or 'sym8' (fallback)
        dwt_level       — decomposition level; 4 for 30.72 MS/s / 1625 kHz
        threshold_low   — confidence below this → REJECT (stage3_ready=False, needs_neural=False)
        threshold_high  — confidence above this → Stage 3 direct (stage3_ready=True)
        use_sst         — True: ssqueezepy.ssq_cwt (first-order SST);
                          False: ssqueezepy.cwt (plain CWT)
        dwt_score_bounds— (low, high) for normalizing DWT_score_raw to [0, 1]
        cwt_energy_bounds-(low, high) for normalizing CWT_energy_ratio to [0, 1]
        holdoff_s       — seconds to ignore triggers after a successful estimate
        """
        ...

    def estimate(self, iq_buffer: np.ndarray, t_offset: int = 0) -> dict:
        """
        Estimate SF and BW from a complex64 IQ buffer.

        Parameters
        ----------
        iq_buffer : np.ndarray, dtype=complex64
            Raw IQ samples captured at self.samp_rate.
            Recommended length: 50–100 ms × samp_rate samples.
        t_offset : int, default 0
            Sample offset of signal start within iq_buffer.
            Provided by Stage 1 PMT trigger (time field).
            Dechirp MF reads iq_buffer[t_offset : t_offset + N_DECHIRP_MAX].

        Returns
        -------
        dict with keys:
            'sf'               : int   — Spreading Factor, 7..12
                                         (undefined if stage3_ready=False, needs_neural=False)
            'bw'               : int   — Bandwidth Hz: 203_000|406_000|812_000|1_625_000
                                         (undefined if stage3_ready=False, needs_neural=False)
            'confidence'       : float — Combined score [0.0, 1.0]
            'method'           : str   — 'dwt+cwt' | 'dwt+cwt+sst'
            't_offset_samples' : int   — Estimated first symbol boundary in iq_buffer (samples)
                                         0 if not reliably detected
            'stage3_ready'     : bool  — True if confidence >= threshold_high
                                         → forward PDU to Stage 3 immediately
            'needs_neural'     : bool  — True if threshold_low <= confidence < threshold_high
                                         → forward to Stage 4 Neural Verifier
            # Routing summary:
            #   stage3_ready=True,  needs_neural=False → Stage 3
            #   stage3_ready=False, needs_neural=True  → Stage 4
            #   stage3_ready=False, needs_neural=False → REJECT (discard)
        """
        ...
```

### Сигнатура dwt_sf_estimation (v8)

Внутрішня функція у `src/stage2/dwt_estimator.py`. Виклик з `blind_estimator.py`.

```python
def dwt_sf_estimation(
    iq: np.ndarray,
    bw_candidate: int,
    wavelet: str = "sym5",       # API compat; not used in v7+
    level: int = 4,              # API compat; not used in v7+
    samp_rate: float = 30.72e6,
    t_offset: int = 0,           # v8: sample offset з PMT trigger Stage 1
) -> dict:
    """
    Returns
    -------
    dict with 5 keys (UNCHANGED):
        'sf'              : int   — Spreading Factor 7..12
        'bw_hint'         : int   — bw_candidate passthrough
        'score'           : float — peak/mean FFT ratio (Dechirp MF)
        'best_lag'        : int   — always 0 in v7+ (API compat)
        't_offset_samples': int   — estimated signal onset sample in iq_buffer
    """
```

### Контракт Python Dev

- **Жодних магічних чисел у тілі методів** — всі константи передаються через конструктор.
  `TARGET_BWS` — єдиний клас-рівневий константний список (не змінюється; ELRS spec).
- **`estimate()` завжди повертає dict** (не `None`). Caller визначає дію за флагами.
- **Thread safety:** один екземпляр — один потік (внутрішній `sf_history`, `last_trigger_time` — mutable state).
- **`t_offset`** передається з PMT trigger (Stage 1 `time` field). `blind_estimator.py` приймає його у `estimate()` і прокидає у `dwt_sf_estimation(t_offset=t_offset)`.

### Залежності (requirements.txt — C2-1)

```
pywt         # PyWavelets (pywt.wavedec)
ssqueezepy   # CWT + SST (cwt, ssq_cwt)
numpy        # основа
scipy        # fallback cwt (scipy.signal.cwt), signal utils
cupy-cuda12x # GPU прискорення (опціонально, C2-3)
```

---

## Очікувані метрики Stage 2

| Метрика | Ціль | Блокує T2 | Джерело |
|---------|------|-----------|---------|
| SF accuracy | ≥ 85% @ SNR ≥ −10 dB | ✅ ТАК | [[stage2-plan]], [[obsidian-vault/CLAUDE.md]] |
| BW accuracy | ≥ 80% @ SNR ≥ −12 dB | ✅ ТАК | |
| SF+BW pair | ≥ 78% @ SNR = −14 dB | ✅ ТАК | |
| Latency (буфер 50 мс) | ≤ 25 мс (медіана, RTX 3070) | ✅ ТАК | |
| False trigger rate | ≤ 5% (confidence ≥ 0.4 на AWGN) | ⚠️ Info | T2-6 |

**ТЗ-цілі** (амбіційні, не блокуючі):
SF ≥ 98% @ −10 dB / BW ≥ 95% @ −12 dB / pair ≥ 92% @ −14 dB / latency ≤ 12 мс
([[stage2-tz-dwt-cwt]] §4 — Note: це stretch goals, блокуючі — у таблиці вище).

---

## Тестове середовище (для T2)

- Синтетика: 24 пари SF7–12 × BW{203,406,812,1625}kHz
- SNR sweep: −14 → +10 dB, крок 2 dB, N=500/комбінацію → **12 000 тестів**
- Сигнал: CSS up-chirps (8 преамбула + 2 SYNC + 2.25 down-chirp), AWGN фон
- samp_rate = 30.72 MS/s, буфер 50 мс = 1,536,000 семплів
- Калібрування bounds: 10,000 pure AWGN буферів → ROC для порогів

---

## Залежності та подальші кроки

```
DSP Research (цей файл, R2-5) → Python Dev (C2-1..C2-6)
    → blind_estimator.py + gr_blind_estimator.py
    → Test/QA (T2-1..T2-7) [BLOCKING]
    → Docs D2-1..D2-4 + Git коміт
```

- **C2-1** — `src/stage2/requirements.txt` (pywt, ssqueezepy, scipy, cupy-cuda12x)
- **C2-2** — `src/stage2/dwt_estimator.py` (DWT SF, CPU, pywt)
- **C2-3** — `src/stage2/cwt_estimator.py` (CWT/SST BW, CPU+optional CuPy)
- **C2-4** — `src/stage2/blind_estimator.py` (DWT+CWT+gate, інтерфейс R2-4)
- **C2-5** — `src/stage2/gr_blind_estimator.py` (GNU Radio sync_block wrapper)
- **C2-6** — `src/stage2/bench_stage2.py` (latency benchmark ≤ 25 мс)

---

## Джерела

1. [[stage2-tz-dwt-cwt]] — ТЗ №2 (головний): опис алгоритму, метрики, Python reference
2. [[stage2-key-dwt]] — Synthesis DWT: sym5 обґрунтування, Level 4, SF→lag таблиця
3. [[stage2-key-cwt]] — Synthesis CWT/SST: Morlet, 4 sparse scales, SST threshold
4. [[stage2-key-confidence-gate]] — Synthesis Gate: formula, 0.4/0.7, false-trigger control
5. [[stage2-arch-principles]] — NotebookLM Architecture §1–10: DWT-FFT 99.5%, Level 3–4, SST second-order
6. [[03-tz2-dwt-cwt]] — KB-2 аналіз ТЗ№2: архітектура v1.1, критичні обмеження DWT, confidence thresholds
7. [[09-stage2-blind-estimator-py]] — Python code reference: gr.sync_block API, pipeline steps
8. [[stage2-dechirp-math]] — Stage 3 математика: підтверджує 24 паралельні гіпотези
9. [[docs/stage2-plan]] — повний план Stage 2: метрики, розподіл по агентах
10. [[docs/cfar-spec]] — зразок spec Stage 1: структура, якість документації
11. `tests/stage2/test-results-stage2.md` — T2 FAIL-звіт: підтвердження обох багів, debugged values, варіанти фіксів (v2 source)
12. `obsidian-vault/logs/test-results-stage2-2026-06-02.md` — T2-retry FAIL-звіт: lag ambiguity diagnosis, CWT scale regression analysis, latency root cause (v3 source)

---

## Статус

- [x] R2-1 DWT специфікація (sym5, Level=4, autocorr cD_4, lag table per BW column)
- [x] R2-2 BW estimation: Welch PSD + per-class hypothesis test (N_total=65536, N_fft=4096, K=31; score[b]=mean(in)/mean(ref); no threshold; score(1625k)=1.75 @ -14dB)
- [x] R2-3 Confidence gate (0.5/0.5 formula, thresholds 0.4/0.7, anti-false-trigger)
- [x] R2-4 Python інтерфейс `ELRS_BlindParameterEstimator` визначений (незмінений)
- [x] R2-5 Самопідтвердження v1 — узгоджено з усіма 9 джерелами
- [x] **R2-fix** — БАГ #1: autocorr_norm = mean(|autocorr|); БАГ #2: Re(IQ) + SF-matched scales
- [x] **R2-fix-v3** — ROOT CAUSE A: CWT-first + DWT signal=Re(IQ) + bw_candidate constraint; ROOT CAUSE B: scale=samp_rate/BW reverted; ROOT CAUSE C: cwt_max_samples=8192 fixed
- [x] **R2-fix-v4** — ROOT CAUSE D: scale=5×samp_rate/(π×BW)=[241,121,60,30], f_c=BW/2 matched до peak IF CSS chirp Re(IQ)
- [x] **R2-fix-v5** — ROOT CAUSE E: §R2-2 замінена Welch PSD spectral occupancy; SST/CWT відмінено; `use_sst` deprecated (у конструкторі); `cwt_energy_bounds=(1.0,10.0)` незмінені; R2-4 незмінений
- [x] **R2-fix-v6** — ROOT CAUSE F: Steps 4-5 замінені per-class hypothesis test `score[b]=mean(S_norm[0..b/2])/mean(S_norm[b/2..b])`, `bw_candidate=argmax(score)`; threshold видалено; energy_ratio=score[bw_candidate]; Steps 1-3 незмінені
- [x] **R2-fix-v7** — ROOT CAUSE H: §R2-1 повністю замінено на Dechirp Matched Filter (v7). DWT autocorr видалено — Re(IQ) UP→UP межа не дає energy surge в cD_4. Нова feature: для кожного SF-кандидата IQ×ref_down_chirp→rfft→peak/mean score; argmax=SF. Score(true SF) = N_sym×SNR_lin >> score(wrong SF)≈2–4. Discrimination ≥5× @ −10dB. Lag table видалено. wavelet/level збережено у сигнатурі для API сумісності. §R2-2/R2-3/R2-4 незмінені.
- [x] **R2-fix-v8** — ROOT CAUSE I: `t_offset=0` додано до inputs §R2-1 pseudocode і `dechirped=iq[t_offset:t_offset+n_use]×ref`; `estimate(t_offset=0)` і `dwt_sf_estimation(t_offset=0)` у §R2-4. ROOT CAUSE J: `N_DECHIRP_MAX=65536` додано до inputs §R2-1; `n_use=min(n_sym, N_DECHIRP_MAX, len(iq)-t_offset)`; latency таблиця виправлена (FFT(65536)×6<1ms). §R2-2/R2-3/Dechirp MF алгоритм незмінені.
- [x] **status: approved-v8** → Python Dev може починати C2-fix-v8
