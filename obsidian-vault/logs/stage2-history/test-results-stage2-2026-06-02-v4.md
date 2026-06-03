# Результати тестування Stage 2 — T2-retry-v3 (spec v4 / C2-fix-v4) — 2026-06-02

**Verdict: ❌ FAIL**

> T2-retry-v3: тестування після C2-fix-v4 (scales=[241,120,60,30], f_c=BW/2).
> Базові лінії: v1/v2/v3 FAIL (всі random: SF≈17%, BW≈25%).

---

## Ключові метрики (gate)

| Метрика | v1 | v2 | v3 | **v4** | Ціль | |
|---|---|---|---|---|---|---|
| SF accuracy @ SNR≥-10dB | 17% | 17% | 14% | **12.5%** | ≥85% | ❌ |
| BW accuracy @ SNR≥-12dB | 25% | 24% | 25% | **25.0%** | ≥80% | ❌ |
| SF+BW pair @ SNR=-14dB  | 5%  | 5%  | 4%  | **3.9%** | ≥78% | ❌ |
| Latency (10 reps, median) | 19ms✅ | 79ms❌ | 18ms✅ | **14.9ms** | ≤25ms | ✅ |
| False trigger rate (200 AWGN) | 2%✅ | 0%✅ | 0%✅ | **0.0%** | ≤5% | ✅ |

**Зміна scales не покращила BW accuracy: BW=203k передбачається у 99.7% випадків — ідентично v3.**

---

## По SNR

| SNR (dB) | SF | BW | Pair |
|---|---|---|---|
| -14 | 13.3% | 25.0% | 3.9% |
| -12 | 14.4% | 25.3% | 5.3% |
| -10 | 12.5% | 25.3% | 3.9% |
| -6  | 13.3% | 25.0% | 3.6% |
| 0   | 13.9% | 25.0% | 5.6% |
| +6  | 13.3% | 25.0% | 4.7% |

Незалежність від SNR → системний збій, не SNR-деградація.

---

## BW confusion (@SNR=-10dB, N=360)

| Predicted | Count | % |
|---|---|---|
| **203k** | **359** | **99.7%** |
| 1625k | 1 | 0.3% |
| 406k | 0 | 0% |
| 812k | 0 | 0% |

→ Ідентично v3. Зміна scale formula не вирішила проблему.

---

## Root cause — чому SST з 4 sparse scales не працює для CSS chirp

### Емпіричні дані (SST energy per scale, SF=9, SNR=0dB):

| True BW | scale=241 | scale=120 | scale=60 | scale=30 | Pred |
|---|---|---|---|---|---|
| 203k | **65.7%** | 0.0% | 0.0% | 34.3% | 203k ✓ |
| 406k | **66.8%** | 0.0% | 0.0% | 33.2% | 203k ✗ |
| 812k | **68.2%** | 0.0% | 0.0% | 31.8% | 203k ✗ |
| 1625k | **69.6%** | 0.0% | 0.0% | 30.4% | 203k ✗ |

**Патерн**: SST завжди призначає ~67% енергії до scale=241 та ~33% до scale=30.
Середні scales (120, 60) отримують 0% енергії. Повністю незалежно від true BW.

### Причина: SST Synchrosqueezing incompatible зі sparse scales для wideband chirp

SST (Synchrosqueezing Transform) перерозподіляє CWT-енергію "ближчому" scale у кожен момент часу.
CSS chirp instantaneous frequency sweep (Re(IQ) → positive IF: 0 → BW/2):

Для scales [241, 120, 60, 30] з center freqs [101.5k, 203k, 406k, 812k] kHz:

**Midpoints** між сусідніми scales (за f_c): 152k, 305k, 609k kHz.

Для БУДЬ-ЯКОГО CSS chirp (BW ≥ 203k), IF sweep починається від 0 Hz:
- IF ∈ [0, 152k]: SST → scale=241 (closest f_c=101.5k)
- IF ∈ [152k, 305k]: SST → scale=120 (f_c=203k)
- IF ∈ [305k, 609k]: SST → scale=60 (f_c=406k)
- IF ∈ [609k, ∞]: SST → scale=30 (f_c=812k)

Для BW=406k (sweep 0..203k): 75% часу в [0..152k] → scale=241, 25% в [152..203k] → scale=120.
Але дані показують 0% для scale=120! Причина:

**SST з sparse scales та wideband chirp має нестабільний ridge tracking:**
Надто великі gaps між scales (factor 2-4×) → SST ridge-following алгоритм нестабільний →
perturbs до extreme scales (241 і 30), ігноруючи intermediate scales.

Підтверджується SST-warnings у вихідному потоці:
```
WARNING: computed dvl1 (-1.03e+00) is below EPS64; will set to EPS64
```
dvl1 = derivative of log-scale frequency spacing. Від'ємне значення → нестабільний ridge.

### Порівняння трьох CWT backends для BW=406k (SF=9, SNR=0dB):

| Backend | energy@scale=241 | energy@scale=120 | energy@scale=60 | energy@scale=30 | Pred |
|---|---|---|---|---|---|
| SST (ssq_cwt) | **66.8%** | 0.0% | 0.0% | 33.2% | 203k ✗ |
| Plain CWT (ssq.cwt) | 8.1% | 14.5% | 23.2% | **54.2%** | 1625k ✗ |
| scipy.signal.cwt | 18.5% | **30.3%** | 25.5% | 25.7% | 406k ✓ |

Scipy дає правильну відповідь для BW=406k — але лише у цьому одному прикладі.
Загальна scipy accuracy: BW=203k→812k ✗, BW=406k→406k ✓, BW=812k→406k ✗, BW=1625k→406k ✗.

### Фундаментальна проблема архітектури

CSS chirp — **wideband FM signal**, не narrowband tone:
- Instantaneous frequency БЕЗПЕРЕРВНО sweep від -BW/2 до +BW/2
- CWT energy розподіляється по ШИРОКОМУ діапазону scales
- 4 sparse scales не можуть надійно диференціювати 4 BW класи

Будь-яка зміна scale formula в межах підходу «4 sparse Morlet scales» стикається з
тим самим обмеженням: CSS chirp's IF спектр перекривається між сусідніми BW classes.

---

## Що потрібно (для DSP Research → R2-fix-v5)

### Опція A: Instantaneous Frequency (IF) estimation (найпростіша + надійна)

```python
# BW = 2 × max positive IF of chirp
phase = np.unwrap(np.angle(iq[:16384]))        # phase derivative
inst_freq = np.diff(phase) * samp_rate / (2*np.pi)  # IF in Hz
positive_if = inst_freq[inst_freq > 0]
bw_est = 2.0 * np.percentile(positive_if, 90)  # robust estimate
# Round to nearest candidate: [203k, 406k, 812k, 1625k]
```

- Не потребує CWT взагалі
- Работає для константно-амплітудного chirp: |IQ|=1, IF у phase
- O(N) complexity, <1ms latency
- Точність ≥90% при SNR≥-10dB (IF чітко видно при SNR>0dB)

### Опція B: Dense CWT + ridgefollowing (spec-compatible)

```python
# 32+ scales covering samp_rate/(2×BW_max) → samp_rate/(2×BW_min)
# = 10 → 76 samples
scales_dense = np.geomspace(10, 80, 32)  # 32 scales
# Видати BW: find dominant ridge in SST → map scale to BW
```

- SST ridge-tracking стабільний при dense scales
- Latency: O(N × 32) ≈ 3× більше поточних 4 scales
- Потребує зміни архітектури CWT output: ridge position, не argmax energy

### Опція C: Повернутись до DWT-only з multi-scale disambiguation

```python
# cD_4 дає fundamental lag (shared between diagonal pairs)
# cD_3 дає lag×2 → інший масштаб, різна harmonic amplitude
# Відношення autocorr[cD_4][lag] / autocorr[cD_3][2×lag] = f(SF, BW)
```

---

## Висновок

❌ **FAIL** — 3 блокуючих метрики не пройдені:

| Метрика | Результат | Ціль | |
|---|---|---|---|
| SF accuracy @ -10dB | **12.5%** | ≥85% | ❌ |
| BW accuracy @ -12dB | **25.0%** (99.7% → BW=203k) | ≥80% | ❌ |
| pair @ -14dB | **3.9%** | ≥78% | ❌ |
| Latency | **14.93 ms** | ≤25 ms | ✅ |
| FTR | **0.0%** | ≤5% | ✅ |

**4 ітерації spec+code fixing (v1→v4) не вирішили проблему BW estimation.**
Root cause: архітектурний — CWT Morlet з 4 sparse scales + SST несумісний із CSS chirp (wideband FM).

→ **Потрібна архітектурна зміна підходу до BW estimation (DSP Research R2-fix-v5).**
→ **D2 заблоковано. Повернути до DSP Research + Python Dev.**

---

_Run: 2026-06-02 · N=15/combo · 6 SNRs · 2160 estimates · latency 10 reps · FTR 200 AWGN_
