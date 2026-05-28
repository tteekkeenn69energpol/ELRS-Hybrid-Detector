---
tags: [overview, project, stage-1]
created: 2026-05-28
updated: 2026-05-28
agent: docs
status: stage-1-done
step: D-1a
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

## Roadmap (Stage 1 → 2 → 3 → 4)

Повний каскад описано у [[../docs/pipeline-overview|pipeline-overview]].

| Stage | Назва | Стан |
|---|---|---|
| 1 | 2D OS-CFAR trigger (C++/AVX2) | ✅ Done (2026-05-28) |
| 2 | Blind Parameter Estimator (DWT/CWT, Python/CuPy) | ⏳ Planned |
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
- [[../logs/progress-snapshots/2026-05-28-stage1-done|2026-05-28-stage1-done]] — snapshot PROGRESS.md
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
- [[../docs/pipeline-overview]]
- [[../logs/decisions-log]]
- [[../logs/test-results-2026-05-28]]
- [[../research/sources]]
