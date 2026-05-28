---
tags: [docs, decisions, log, stage-1]
created: 2026-05-28
updated: 2026-05-28
agent: docs
status: active
step: D-1c
---

# Лог рішень — ELRS Hybrid Detector

> Консолідований лог процесних та алгоритмічних рішень.
> Джерело істини для процесних рішень: `PROGRESS.md` § «Лог рішень».
> Цей файл розширює лог алгоритмічними обґрунтуваннями зі специфікації
> [[../docs/cfar-spec|cfar-spec]] та QA-вердиктом
> [[test-results-2026-05-28|test-results-2026-05-28]].

---

## Процесні рішення (Stage 1)

| # | Дата | Агент | Рішення |
|---|------|-------|---------|
| P-01 | 2026-05-28 | Orchestrator | Призначено KB-1 → Knowledge Builder (старт Фази 0) |
| P-02 | 2026-05-28 | Knowledge Builder | KB-2: 19 Google Drive docs розпарсено → `/research/` + [[../research/sources]]; [[../docs/pipeline-overview|pipeline-overview]] створено |
| P-03 | 2026-05-28 | Orchestrator | KB-1…KB-6 закрито (Фаза 0 done). Призначено R-1 → DSP Research |
| P-04 | 2026-05-28 | DSP Research | R-1..R-4 done. Параметри: N_guard=4×2, N_ref=16×8, k=612, threshold_db=12.5, min_snr_db=7.0 (див. A-01..A-05) |
| P-05 | 2026-05-28 | Orchestrator | R-1..R-4 закрито (spec approved). Призначено C-1 → C++ Dev |
| P-06 | 2026-05-28 | C++ Dev | C-1..C-5 done. Commit `308f60d`. Throughput 89.96 MS/s (20 threads) / 14.10 MS/s single |
| P-07 | 2026-05-28 | Orchestrator | C-1..C-5 закрито. Призначено T-1 → Test/QA (БЛОКУЮЧИЙ gate) |
| P-08 | 2026-05-28 | Test/QA | T-1..T-6 done. **PASS**. Pfa MC=0/10.5M (analytic 3.55e-11) ≤ 1% ✅; Thrpt parallel=86.27 MS/s ≥ 80 ✅; Pd=1.0 @ SNR=−6 dB. Артефакти у `/tests/` + [[test-results-2026-05-28]]. Commit `e3668ec`. |
| P-09 | 2026-05-28 | Orchestrator | T-6 PASS верифіковано (commit `e3668ec`, `/src/` недоторкано). Призначено D-1 → Docs (фінал Stage 1) |
| P-10 | 2026-05-28 | Docs | D-1..D-4 done. Створено [[../00-overview/project-overview]], [[../00-overview/architecture]], [[decisions-log]], [[progress-snapshots/2026-05-28-stage1-done]], `/README.md`. PROGRESS.md закрито Stage 1. |
| P-11 | 2026-05-28 | Knowledge Builder | **KB-extra**: 40 зовнішніх посилань оброблено → `research/ext-*.md`. Категорії: cfar-theory(8), lora-detection(3), drone-rf(6), cuda-gpu(8), github-cfar(6), github-gnuradio(3), ml-rf(4), fmcw(2). 3 дублікати виявлено й пропущено (stubs з redirect: ext-drone-rf-12 → [[../research/23-flak-czyba-distributed-sensor-grid]], ext-drone-rf-17 → [[../research/24-sorecau-wideband-usrp-rfnoc]], ext-fmcw-40 → [[../research/25-venter-sdr-pulse-doppler-gpu]]). Status: ready for Stage 2+ reference. Index — [[../research/sources#external-references-kb-extra-2026-05-28-40-зовнішніх-посилань\|sources § External References]]. |
| P-12 | 2026-05-28 | Docs | KB-extra sync + vault hygiene commit. Додано `/.gitignore` (.obsidian/, build/, *.so, __pycache__/, data/raw/). Перенесено `/kb-extra-links-command.md` → `obsidian-vault/logs/`. Усі untracked .md у `obsidian-vault/` додано поіменно (без `git add -A`). Repo тепер повністю tracked. Ready for Stage 2. |

---

## Алгоритмічні рішення (Stage 1)

Деталі та джерела — у [[../docs/cfar-spec|cfar-spec]] §34-47 (власність DSP Research, не змінюється Docs-агентом).

### A-01 — OS-CFAR замість CA-CFAR

- **Агент:** DSP Research (R-1)
- **Дата:** 2026-05-28
- **Рішення:** використати **2D Ordered-Statistic CFAR** на спектрограмі (час × частота).
- **Чому:** ELRS-FHSS в ISM 915 MHz має кілька одночасних передавачів + імпульсні
  завади (WiFi/BT). CA-CFAR усереднює викиди → поріг роздувається → `Pd → 0`.
  OS-CFAR ігнорує до `(N_ref − k)` викидів і утримує `Pd ≈ 0.58` у тих самих
  умовах (`[[../research/dataset-cfar]]` §1).
- **CFAR-loss vs CA-CFAR (homogeneous):** ≤ +0.53 dB (інформаційно).
- **Джерела:** [[../research/cfar email|cfar email]], [[../research/dataset-cfar]],
  [[../research/17-gpu-stft-cfar-analysis]], [[../research/21-os-cfar-realtime-impl]].

### A-02 — Параметри вікна N_ref=16×8, N_guard=4×2

- **Агент:** DSP Research (R-1)
- **Рішення:**
  - `N_ref_f = 16` — тренувальних комірок по частоті (стабільна оцінка ISM-шуму).
  - `N_ref_t = 8` — тренувальних по часу (баланс throughput vs точність).
  - `N_guard_f = 4` — захист від self-masking основної лопаті чирпу.
  - `N_guard_t = 2` — преамбула ELRS = 8 up-chirps, 2 кадрів охорони достатньо.
- **Похідне:** `N_train_total = (2·16+2·4+1)·(2·8+2·2+1) − (2·4+1)·(2·2+1) = 41·21 − 9·5 = 816`.
- **Консенсус 5 джерел:** [[../research/17-gpu-stft-cfar-analysis]] (train 16×8, guard 4×2),
  [[../research/cfar email|cfar email]] (train 12–16, GC 4–6), [[../research/dataset-cfar]].

### A-03 — rank_percent = 0.75 → k = 612

- **Агент:** DSP Research (R-1)
- **Рішення:** `k = round(0.75 · N_train_total) = round(0.75 · 816) = 612`.
- **Чому:** 75-й перцентиль ігнорує до 25% завадних комірок — консенсус усіх 5 джерел:
  - `[[../research/dataset-cfar]]`: k ≈ ¾·N_T;
  - `[[../research/17-gpu-stft-cfar-analysis]]`: rank 0.75;
  - `[[../research/cfar email|cfar email]]`: 0.75–0.82.
- **Тюнінг-діапазон:** експоновано в API як `float rank_percent ∈ [0.5, 0.95]`.

### A-04 — Threshold 12.5 dB (Detection Gap, α ≈ 17.78)

- **Агент:** DSP Research (R-1)
- **Рішення:** `threshold_db = 12.5` (linear `α = 10^(thr/10) = 17.7828`).
- **Чому:** робочий стартовий поріг з [[../research/cfar email|cfar email]] §2.2.
  Аналітично дає Pfa ≈ 3.55e-11 при N=816, k=612 (формула:
  `P_fa = Π_{i=1..k} (N+1−i)/(N+1−i+α)`, [[../research/dataset-cfar]] §2).
- **Тюнінг-діапазон:** 11–14 dB. Підтверджено Test/QA: при thr ∈ [6, 20] dB
  MC↔analytic узгоджені у межах ±20% у робочому діапазоні (≤ 10 dB), і обидва
  < noise floor при thr ≥ 11 dB ([[test-results-2026-05-28]] ROC table).

### A-05 — min_snr_db = 7.0 (hard floor)

- **Агент:** DSP Research (R-1)
- **Рішення:** додатковий жорсткий поріг: навіть якщо CFAR пройшов, CUT із SNR
  < 7 dB відкидається.
- **Чому:** [[../research/cfar email|cfar email]] §2.2 — захист від residual-noise
  detections при роздутих X(k) у завадному середовищі.

### A-06 — rank-only реалізація через std::nth_element

- **Агент:** DSP Research → C++ Dev (R-1 → C-1)
- **Рішення:** не сортувати весь вектор reference-комірок; використати
  `std::nth_element` (O(N) середнє) або partial-sort.
- **Чому:** ключова оптимізація з [[../research/21-os-cfar-realtime-impl]]
  (Bales et al., GTRI/AFRL). Економить ~3-5× CPU vs повний std::sort.
- **Реалізація (C++ Dev, C-2):** count-rank pre-filter (рахунок елементів
  ≤ candidate), материалізація X(k) лише на CUT-pass.

### A-07 — Row-stripe tiling, 1 instance per thread

- **Агент:** C++ Dev (C-3)
- **Рішення:** багатопотоковість через **декілька екземплярів CFAR2D**, по
  тайлах матриці (row-stripe).
- **Чому:** thread-safety контракт спеки [[../docs/cfar-spec|cfar-spec]] §134:
  один екземпляр = один потік. Без блокувань на гарячому шляху.
- **Результат:** speedup parallel/single = **6.4×** на 20 логічних ядрах
  (86.27 MS/s ÷ 13.53 MS/s, [[test-results-2026-05-28]]).

### A-08 — AVX2 SIMD (без CUDA на Stage 1)

- **Агент:** C++ Dev (C-2)
- **Рішення:** використати AVX2 intrinsics (`-O3 -mavx2 -march=native -ffast-math`).
- **Чому:** Stage 1 ціль — Lab-PC implementation; CUDA-міграція винесена у
  Stage 1.5 (опціонально, див. [[../research/17-gpu-stft-cfar-analysis]]).
- **Layout:** row-major (час — рядок, частота — стовпець) для coalesced доступу
  та сумісності з майбутньою CUDA-міграцією.

---

## KB-extra (2026-05-28)

Re-активація Knowledge Builder для індексації 40 зовнішніх посилань
(після Stage 1 PASS). Артефакти — `obsidian-vault/research/ext-*.md`
(40 файлів, 8 категорій), індекс — [[../research/sources|sources § External References]].

Категорії: cfar-theory (8), lora-detection (3), drone-rf (6), cuda-gpu (8),
github-cfar (6), github-gnuradio (3), ml-rf (4), fmcw (2).

**Дублікати (3, stubs з redirect):**
- `ext-drone-rf-12` → [[../research/23-flak-czyba-distributed-sensor-grid]]
- `ext-drone-rf-17` → [[../research/24-sorecau-wideband-usrp-rfnoc]]
- `ext-fmcw-40` → [[../research/25-venter-sdr-pulse-doppler-gpu]]

**Статистика:** 33 done · 4 partial (paywall/anti-bot) · 1 unavailable (404).
2 PDF додано у `data/raw/pdf/` (виключено з git через `.gitignore data/raw/`).

Статус: ready for Stage 2+ reference (Blind Estimator / Dechirp / Neural Verifier).

---

## Невирішені / Stage 2+ питання

- **Q-01:** Pfa-ціль ТЗ (10⁻⁴ при Pd > 0.92, SNR=−6 dB) — інформаційно для Stage 2+.
  Stage 1 закрив тільки Pfa ≤ 1%.
- **Q-02:** Реальні IQ-записи з SPECTRAN V6 — не використано на Stage 1
  (тільки синтетика). Перенесено у Stage 2+.
- **Q-03:** CUDA-міграція через CuPy `rank_filter` або кастомний bitonic-sort kernel —
  опціональний Stage 1.5.
- **Q-04:** 45 відкритих дослідницьких питань — [[../research/18-research-questions]].

---

## Посилання

- [[../docs/cfar-spec]] — повна специфікація OS-CFAR (DSP Research, approved)
- [[test-results-2026-05-28]] — QA-вердикт Stage 1 (PASS)
- [[progress-snapshots/2026-05-28-stage1-done]] — snapshot PROGRESS.md
- [[../00-overview/project-overview]]
- [[../00-overview/architecture]]
- [[../research/sources]] — джерела KB-2
