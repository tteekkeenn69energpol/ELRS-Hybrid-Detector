# ELRS Hybrid Detector — Stage 1 + Stage 2

> Каскадний пайплайн виявлення, класифікації та картування **ELRS frequency-hopping
> spread-spectrum (FHSS)** трафіку у смузі ISM 915 MHz.
> Розробляється мультиагентною системою на **Claude Code** (6 агентів).

**Stage 1:** ✅ **DONE** (2026-05-28) — Pfa = 0 / 10.5M cells, Throughput = 86.27 MS/s.
**Stage 2:** ✅ **DONE** (2026-06-03) — SF=91.9%, BW=94.9%, Pair=95.8%, Latency=11.4ms.

---

## Що це

`ELRS Hybrid Detector` — Stage 1 модуль реалізує **2D Ordered-Statistic CFAR**
детектор сигналів у спектрограмі (час × частота), отриманій із
SoapyAaronia / SPECTRAN V6 при `samp_rate = 30.72 MS/s`, `center = 915 MHz`.

Алгоритм (повна спека: `obsidian-vault/docs/cfar-spec.md`):

```
IQ source → Stream-to-Vector(fft_size=2048)
          → FFT(shift=True, BlackmanHarris)
          → Complex-to-Mag² (vlen=2048)
          → CFAR2D (N_ref=16×8, N_guard=4×2, k=612, thr=12.5 dB, min_snr=7 dB)
          → PMT detection {t_idx, f_idx, power_db, snr_db}
```

OS-CFAR (а не CA-CFAR) обрано тому, що в ISM 915 MHz одночасно присутні
кілька передавачів та імпульсні завади (WiFi/BT) — CA-CFAR розмиває поріг,
OS-CFAR ігнорує до 25% «викидів» (rank=0.75 → k=612 із N=816 тренувальних комірок).
Деталі рішення: `obsidian-vault/logs/decisions-log.md` § A-01..A-08.

## Структура репозиторію

```
/
├── src/                              ← Stage 1 C++ implementation
│   ├── cfar2d.hpp / cfar2d.cpp       ← OS-CFAR ядро (AVX2, rank-only)
│   ├── bench_main.cpp                ← throughput benchmark
│   ├── CMakeLists.txt                ← -O3 -mavx2 -march=native -ffast-math
│   └── build/
├── tests/                            ← Test/QA gate (blocking)
│   ├── run.sh                        ← entry point: build → MC → ROC → plot → report
│   ├── synth.py                      ← AWGN + ELRS chirp synthesizer
│   ├── test_cfar2d.py                ← Python driver (Pfa MC, ROC, Pd, throughput)
│   ├── cfar2d_c.cpp / build_lib.sh   ← C-ABI shim + libcfar2d_c.so build
│   ├── plot_and_report.py            ← post-processing + markdown report
│   └── test-results.{md,json,png}    ← signed Stage 1 verdict (2026-05-28)
├── obsidian-vault/                   ← knowledge base (Obsidian)
│   ├── CLAUDE.md                     ← shared agent rules
│   ├── PROGRESS.md                   ← live checklist (single source of truth)
│   ├── 00-overview/
│   │   ├── project-overview.md       ← what / why / current state
│   │   └── architecture.md           ← 6-agent architecture, gate flow
│   ├── docs/
│   │   ├── cfar-spec.md              ← R-1..R-4 spec (DSP Research, approved)
│   │   └── pipeline-overview.md      ← Stage 1..4 cascade
│   ├── research/                     ← 19 KB-2 source documents
│   ├── logs/
│   │   ├── decisions-log.md          ← P-01..P-10 + A-01..A-08
│   │   ├── test-results-2026-05-28.md
│   │   └── progress-snapshots/
│   └── agents/                       ← 6 agent prompts (orchestrator, KB, R, C, T, D)
└── README.md                         ← this file
```

> Додатково на рівні проєкту (поза цим репо): `NEW_CODE/CFAR_2D_ELRS_915_30MSPS_2048.grc`
> (standalone GRC-флоуграф) та `missions/mission_01_cartographer/` (hop-cartographer).
> Див. `/home/tekken/CLAUDE.md`.

## Як зібрати (Stage 1 ядро)

```bash
# C++ ядро + benchmark
cd src
cmake -B build -S .
cmake --build build -j
./build/bench_cfar2d            # standalone throughput bench
```

Деталі прапорів компілятора — у `src/CMakeLists.txt` (`-O3 -mavx2 -march=native -ffast-math`,
GCC 13.3.0 на Ubuntu 24.04).

## Як запустити тести (Test/QA suite)

```bash
cd tests
./run.sh
```

Скрипт виконує (≈ 8 хв на Intel i5-13600KF, 20 threads):

1. Збирає C-ABI shim → `libcfar2d_c.so`.
2. Запускає `test_cfar2d.py`: Monte-Carlo Pfa, ROC sweep (7 SNRs × 11 thresholds),
   Pd-vs-SNR (12 точок × 200 пакетів), throughput-бенчмарк.
3. Генерує `test-results.{json,md,png}` (`plot_and_report.py`).
4. Копіює звіт у `obsidian-vault/logs/test-results-2026-05-28.md`.

---

## Stage 2 — Blind Parameter Estimator (Welch PSD + Dechirp Matched Filter)

**Status:** ✅ Done (2026-06-03). **Verdict: PASS.**

| Метрика | Результат | Ціль | Статус |
|---|---|---|---|
| SF accuracy @ −10 dB | **91.9%** | ≥ 85% | ✅ |
| BW accuracy @ −12 dB | **94.9%** | ≥ 80% | ✅ |
| SF+BW pair @ −14 dB | **95.8%** | ≥ 78% | ✅ |
| Latency (median) | **11.4 ms** | ≤ 25 ms | ✅ |
| False Trigger Rate | **2.0%** | ≤ 5% | ✅ |

### Архітектура

- **BW estimation:** Welch PSD (`N_total=65536`, `N_fft=4096`, K=31 Hann frames) → per-class hypothesis test → `score[b]=mean(S_norm[0..b/2])/mean(S_norm[b/2..b])` → argmax.
- **SF estimation:** Dechirp Matched Filter (6 гіпотез SF7..SF12) → `IQ×ref_down_chirp(sf_hat)` → FFT(`n=n_use`) → peak/mean score → argmax.
- **Confidence gate:** пороги 0.4/0.7, holdoff 100 ms.

### Залежності

```bash
cd src/stage2
pip install -r requirements.txt   # numpy, scipy, pywt
```

Специфікація: `obsidian-vault/docs/stage2-dwt-spec.md` (approved-v8).
Повний QA-звіт: `tests/stage2/test-results-stage2-2026-06-03-v8.md`.

**Known Issue (non-blocking):** SF7/BW=812k @ SNR=−14 dB = 0/50 — BW estimation edge case при екстремально низькому SNR. Загальний pair=95.8% >> 78% target → PASS підтверджено. Зафіксовано для майбутнього виправлення.

---

## Результати Stage 1 (2026-05-28)

| Метрика | Результат | Ціль | Статус |
|---|---|---|---|
| Pfa (MC, default thr=12.5 dB) | **0.000e+00** (0 / 10,485,760) | ≤ 1% | ✅ |
| Pfa (analytic, spec §45) | 3.555e-11 | ≤ 1% | ✅ |
| Throughput (parallel, 20 threads) | **86.27 MS/s** | ≥ 80 MS/s | ✅ |
| Throughput (single-thread) | 13.53 MS/s | (інфо) | — |
| Speedup parallel/single | **6.4×** | (інфо) | — |
| Pd @ SNR=−6 dB | **1.000** | ≥ 0.92 | ✅ |

Повний QA-звіт: `obsidian-vault/logs/test-results-2026-05-28.md`.
Алгоритмічна специфікація: `obsidian-vault/docs/cfar-spec.md`.

Параметри: `N_ref=16×8`, `N_guard=4×2`, `k=612` (rank=0.75), `α=17.78`
(thr=12.5 dB), `min_snr_db=7.0` — консенсус 5 джерел
(`obsidian-vault/research/cfar email.md`, `dataset-cfar.md`,
`17-gpu-stft-cfar-analysis.md`, `21-os-cfar-realtime-impl.md`,
`08-stage1-oscfar-cpp.md`).

## Roadmap

Повний каскад — `obsidian-vault/docs/pipeline-overview.md`.

| Stage | Назва | Стан |
|---|---|---|
| 1 | 2D OS-CFAR trigger (C++/AVX2) | ✅ Done (2026-05-28) |
| 2 | Blind Parameter Estimator (Welch PSD + Dechirp MF, Python) | ✅ Done (2026-06-03) |
| 3 | Dechirp + Matched Filter Bank | ⏳ Planned |
| 4 | Neural Verifier (ONNX, EfficientNet-B3 / ViT-Small) | ⏳ Planned |
| 4.5 | RF Fingerprinting + Decision Fusion + Hop-Map + FHSS Tracker | ⏳ Planned |

**End-to-end цілі:** Pd ≥ 95% @ SNR −12 dB, FAR ≤ 1%, throughput 100 MS/s sustained,
latency ≤ 50 ms.

## Hardware

- **Lab:** Aaronia SPECTRAN V6 + SoapyAaronia (30.72 MS/s native, до 200 MHz BW).
- **Field (планується):** ADRV9009 + Artix-7 + JESD204B (100+ MS/s).
- GNU Radio 3.10.11, GRC YAML flowgraphs, OOT-блоки C++ для Stage 1.

## Документація

- **Специфікація OS-CFAR (Stage 1):** [`obsidian-vault/docs/cfar-spec.md`](obsidian-vault/docs/cfar-spec.md)
- **Специфікація Blind Estimator (Stage 2):** [`obsidian-vault/docs/stage2-dwt-spec.md`](obsidian-vault/docs/stage2-dwt-spec.md)
- **Огляд пайплайну:** [`obsidian-vault/docs/pipeline-overview.md`](obsidian-vault/docs/pipeline-overview.md)
- **Архітектура агентів:** [`obsidian-vault/00-overview/architecture.md`](obsidian-vault/00-overview/architecture.md)
- **Лог рішень:** [`obsidian-vault/logs/decisions-log.md`](obsidian-vault/logs/decisions-log.md)
- **QA звіт Stage 2:** [`tests/stage2/test-results-stage2-2026-06-03-v8.md`](tests/stage2/test-results-stage2-2026-06-03-v8.md)
- **Поточний стан:** [`obsidian-vault/PROGRESS.md`](obsidian-vault/PROGRESS.md)
- **Правила агентів:** [`obsidian-vault/CLAUDE.md`](obsidian-vault/CLAUDE.md)

## Ліцензія

TBD.
