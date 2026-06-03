---
tags: [overview, project, stage-1, stage-2]
created: 2026-05-28
updated: 2026-06-03
agent: docs
status: stage-2-done
step: D2-1
---

# ELRS Hybrid Detector — Project Overview

## Призначення

**ELRS Hybrid Detector** — каскадний пайплайн виявлення, класифікації та картування
ELRS-сумісного frequency-hopping spread-spectrum (FHSS) трафіку у смузі ISM 915 MHz.

Розробляється мультиагентною системою на Claude Code (6 агентів, див. [[architecture]]).
Цільове застосування: лабораторні дослідження FHSS-сигналів та польова робота з ELRS-радіолінками.

## Поточний стан — Stage 1 (✅ DONE)

**Stage 1 — 2D OS-CFAR standalone модуль** — завершено та підтверджено Test/QA 2026-05-28.

| Метрика | Результат | Ціль | Статус |
|---|---|---|---|
| Pfa (MC, default thr=12.5 dB) | 0.000e+00 (0 / 10.5M cells) | ≤ 1% | ✅ |
| Pfa (analytic, spec §45) | 3.555e-11 | ≤ 1% | ✅ |
| Throughput (parallel, 20 threads) | **86.27 MS/s** | ≥ 80 MS/s | ✅ |
| Throughput (single-thread) | 13.53 MS/s | (інфо) | — |
| Pd @ SNR=−6 dB (default thr) | 1.000 | ≥ 0.92 | ✅ |

Алгоритмічні параметри (per [[../docs/cfar-spec|cfar-spec]] §34-47):
`N_ref=16×8`, `N_guard=4×2`, `k=612` (rank=0.75), `threshold=12.5 dB`, `min_snr=7 dB`.

Артефакти:
- `/src/cfar2d.{hpp,cpp}` + `bench_main.cpp` + `CMakeLists.txt`
- `/tests/test-results.{md,json,png}`
- [[../logs/test-results-2026-05-28]] (Test/QA verdict: **PASS**)
- Git commits: `308f60d` (C-1..C-5), `e3668ec` (T-1..T-6)

## Stage 2 — ✅ DONE (2026-06-03)

**Stage 2 — Blind Parameter Estimator** — завершено та підтверджено Test/QA 2026-06-03.
Реалізація: Welch PSD (BW) + Dechirp Matched Filter (SF). Verdict: **PASS** (T2-retry-v8).

| Метрика | Результат | Ціль | Статус |
|---|---|---|---|
| SF accuracy @ SNR=−10 dB | **91.9%** | ≥ 85% | ✅ |
| BW accuracy @ SNR=−12 dB | **94.9%** | ≥ 80% | ✅ |
| SF+BW pair @ SNR=−14 dB | **95.8%** | ≥ 78% | ✅ |
| Latency (median, 50ms buffer) | **11.4 ms** | ≤ 25 ms | ✅ |
| False Trigger Rate | **2.0%** | ≤ 5% | ✅ |

Архітектура (per `docs/stage2-dwt-spec.md` approved-v8):
- **BW estimation:** Welch PSD (`N_total=65536`, `N_fft=4096`, K=31 Hann frames) → per-class hypothesis test → `score[b]=mean(S_norm[0..b/2])/mean(S_norm[b/2..b])` → argmax
- **SF estimation:** Dechirp Matched Filter (6 гіпотез SF7..SF12) → `IQ×ref_down_chirp` → FFT(n=n_use) → peak/mean score → argmax
- **Confidence gate:** пороги 0.4/0.7, holdoff 100 ms

Артефакти:
- `/src/stage2/dwt_estimator.py` — Dechirp MF SF estimation
- `/src/stage2/cwt_estimator.py` — Welch PSD BW estimation
- `/src/stage2/blind_estimator.py` — ELRS_BlindParameterEstimator (7 return keys)
- `/src/stage2/gr_blind_estimator.py` — GNU Radio sync_block wrapper
- [[../logs/test-results-stage2-2026-06-03-v8|test-results-stage2-v8]] (Test/QA verdict: **PASS**)
- Git commits: `a3f5a52` (Stage 2 spec + research materials)

**Known Issue (non-blocking):** SF7/BW=812k @ SNR=−14 dB = 0/50 — BW estimation margin edge case при екстремально низькому SNR. Загальний pair=95.8% >> 78% target → PASS підтверджено. Зафіксовано для майбутнього виправлення.

---

## Roadmap (Stage 1 → 2 → 3 → 4)

Повний каскад описано у [[../docs/pipeline-overview|pipeline-overview]].

| Stage | Назва | Стан |
|---|---|---|
| 1 | 2D OS-CFAR trigger (C++/AVX2) | ✅ Done (2026-05-28) |
| 2 | Blind Parameter Estimator (Welch PSD + Dechirp MF, Python) | ✅ Done (2026-06-03) |
| 3 | Dechirp + Matched Filter Bank | ⏳ Planned |
| 4 | Neural Verifier (ONNX, EfficientNet-B3 / ViT-Small) + RF Fingerprinting | ⏳ Planned |
| 4.5 | Decision Fusion + Hop-Map + FHSS Tracker | ⏳ Planned |

End-to-end цілі (per [[../docs/pipeline-overview|pipeline-overview]]):
Pd ≥ 95% @ SNR −12 dB, FAR ≤ 1%, throughput 100 MS/s sustained, latency ≤ 50 ms.

## Ключові документи

- [[architecture]] — мультиагентна архітектура, hand-off flow, gate-блокування
- [[../docs/cfar-spec|cfar-spec]] — специфікація 2D OS-CFAR (DSP Research)
- [[../docs/pipeline-overview|pipeline-overview]] — повний каскад Stage 1..4
- [[../logs/decisions-log|decisions-log]] — лог всіх алгоритмічних та процесних рішень
- [[../logs/test-results-2026-05-28|test-results-2026-05-28]] — Stage 1 QA verdict
- [[../logs/test-results-stage2-2026-06-03-v8|test-results-stage2-v8]] — Stage 2 QA verdict
- [[../logs/progress-snapshots/2026-05-28-stage1-done|2026-05-28-stage1-done]] — snapshot PROGRESS.md (Stage 1)
- [[../logs/progress-snapshots/2026-06-03-stage2-done|2026-06-03-stage2-done]] — snapshot PROGRESS.md (Stage 2)
- `/PROGRESS.md` — поточний checklist кроків
- `/CLAUDE.md` — спільні правила агентів

## Hardware-контекст

| Елемент | Lab (поточно) | Field (планується) |
|---|---|---|
| RF Frontend | Aaronia SPECTRAN V6 + SoapySDR | ADRV9009 + Artix-7 + JESD204B |
| Instantaneous BW | до 200 MHz | до 200 MHz |
| Sample rate | 30.72 MS/s (native V6) | 100+ MS/s |
| Центральна частота | 915 MHz (ISM) | 915 MHz / multi-band |

GNU Radio 3.10.11, GRC YAML flowgraphs, OOT-блоки на C++ для Stage 1.

## Посилання

- [[architecture]]
- [[../docs/cfar-spec]]
- [[../docs/stage2-dwt-spec]]
- [[../docs/pipeline-overview]]
- [[../logs/decisions-log]]
- [[../logs/test-results-2026-05-28]]
- [[../logs/test-results-stage2-2026-06-03-v8]]
- [[../logs/progress-snapshots/2026-06-03-stage2-done]]
- [[../research/sources]]
