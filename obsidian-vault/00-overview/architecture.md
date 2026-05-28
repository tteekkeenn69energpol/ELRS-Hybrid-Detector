---
tags: [overview, architecture, agents, stage-1]
created: 2026-05-28
updated: 2026-05-28
agent: docs
status: stage-1-done
step: D-1b
---

# Архітектура мультиагентної системи

## Принцип

Один **Оркестратор** + п'ять виконавчих агентів. Жоден агент не виконує
кроки за межами своєї ролі. Test/QA — **блокуючий gate**: без його PASS
наступний крок не відкривається.

Усі агенти читають спільний контекст: `CLAUDE.md`, `PROGRESS.md`,
`/obsidian-vault/`. Стан системи живе у PROGRESS.md, історія рішень — у
[[../logs/decisions-log|decisions-log]], пам'ять артефактів — в Obsidian.

## Таблиця агентів

| Агент              | Префікс | Зона відповідальності                                  | Промпт |
|--------------------|---------|--------------------------------------------------------|--------|
| Orchestrator       | —       | Читає PROGRESS.md, призначає **одного** агента за раз | [[../agents/orchestrator]] |
| Knowledge Builder  | `KB-`   | Одноразова ініціалізація: парсинг джерел, vault init  | [[../agents/knowledge-builder]] |
| DSP Research       | `R-`    | Алгоритмічна специфікація, параметри, формули          | [[../agents/dsp-research]] |
| C++ Dev            | `C-`    | Реалізація DSP-блоків (C++/SIMD/CUDA), benchmarks      | [[../agents/cpp-dev]] |
| Test / QA          | `T-`    | MC Pfa/Pd, ROC, throughput-бенчмарки, **блокуючий gate** | [[../agents/test-qa]] |
| Docs               | `D-`    | Obsidian vault, PROGRESS.md, GitHub README, коміти    | [[../agents/docs]] |

## Hand-off flow (KB → R → C → T → D)

```
   ┌──────────────┐    artefact: research/, docs/
   │ Knowledge    │──────────────────────────────┐
   │ Builder (KB) │  (одноразово, Фаза 0)        │
   └──────────────┘                              ▼
                                          ┌────────────────┐
                                          │  Orchestrator  │◄── reads PROGRESS.md
                                          └──────┬─────────┘
                                                 │ assigns one step
   ┌─────────────────────────────────────────────┴───────────────────┐
   │                                                                 │
   ▼                ▼                ▼               ▼                ▼
┌─────┐         ┌─────┐          ┌─────┐         ┌─────┐          ┌─────┐
│ R-  │ ──spec─►│ C-  │ ──code──►│ T-  │ ──PASS─►│ D-  │ ──sync──►│  GH │
│ DSP │         │ C++ │          │ QA  │ ◄──FAIL─│ Docs│          │ git │
└─────┘         └─────┘          └──┬──┘         └─────┘          └─────┘
                                    │
                                    └── FAIL → back to C- or R-
                                        (gate-блокування)
```

**Правило передачі:** артефакт = коміт у `/src/` або файл у `/obsidian-vault/`.
Без артефакту крок не закривається. Без PASS від T-агента — Orchestrator не
відкриває наступний D-крок.

## Принцип gate-блокування (Test/QA)

1. Кожен `C-N` крок (реалізація) автоматично призначає `T-(N+1)` як **блокуючий**.
2. Test/QA повертає **VERDICT: PASS | FAIL** із числами (Pfa, Pd, throughput).
3. PASS → Orchestrator відкриває наступний крок (зазвичай `D-` або наступний `C-`).
4. FAIL → Orchestrator повертає роботу до C-Dev або DSP Research із конкретною причиною.
5. Docs не запускається доки немає PASS — інакше документація фіксує невалідний стан.

Stage 1 gate: Pfa ≤ 1% **AND** Throughput ≥ 80 MS/s (per [[../docs/cfar-spec|cfar-spec]] §60-67).
Підсумок виконання — у [[../logs/test-results-2026-05-28|test-results-2026-05-28]].

## ASCII-діаграма pipeline Stage 1..4

```
┌────────────────────────────────────────────────────────────────────────┐
│ RF FRONTEND                                                            │
│   Aaronia SPECTRAN V6  ──SoapyAaronia──►  IQ stream (complex64)        │
│   samp_rate = 30.72 MS/s, center = 915 MHz, BW ≤ 200 MHz               │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │
                               ▼  GNU Radio 3.10.11 flowgraph
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 1 — 2D OS-CFAR Trigger          ✅ DONE (2026-05-28)             │
│   IQ → Stream-to-Vector(fft_size=2048, complex)                        │
│      → FFT(shift=True, window=BlackmanHarris)                          │
│      → Complex-to-Mag² (vlen=2048)                                     │
│      → CFAR2D (N_ref=16×8, N_guard=4×2, k=612, α=17.78 / thr=12.5 dB)  │
│   Output: PMT detection {t_idx, f_idx, power_db, snr_db}               │
│   Realized: /src/cfar2d.{hpp,cpp} (AVX2, row-stripe parallel, 20 thr)  │
│   Metrics : Pfa = 0/10.5M ; Thrpt = 86.27 MS/s ; Pd@-6dB = 1.0         │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ PMT trigger (~1-5% of stream)
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 2 — Blind Parameter Estimator   ⏳ PLANNED                       │
│   Coarse CFO → DWT pre-screen → CWT (Morlet) → {sf, bw, conf}          │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 3 — Dechirp + Matched Filter    ⏳ PLANNED                       │
│   Parallel dechirping → FFT peak → Preamble validator                  │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 4 — Neural Verifier (ONNX)      ⏳ PLANNED                       │
│   EfficientNet-B3 / ViT-Small + RF Fingerprinting (Stage 4.5)          │
└──────────────────────────────┬─────────────────────────────────────────┘
                               ▼
                ┌──────────────────────────────┐
                │ Decision Fusion + Hop-Map    │
                │ FHSS Tracker / Jammer Logic  │
                └──────────────────────────────┘
```

Деталі по кожній стадії — у [[../docs/pipeline-overview|pipeline-overview]].

## Конвенції сигнального ланцюга (Hard Rule)

Per `/CLAUDE.md` §3 — порядок блоків ніколи не порушується:

```
IQ source → Stream-to-Vector(fft_size, complex)
          → FFT(shift=True, window=blackmanharris)
          → Complex-to-Mag²(vlen=fft_size)
          → CFAR2D / epy_block (in_sig=[(np.float32, fft_size)])
```

`samp_rate = 30.72e6`, `center_freq = 915e6`, `fft_size = 2048` (CFAR) /
`4096` (mission_01 cartographer).

## Посилання

- [[project-overview]]
- [[../docs/cfar-spec]]
- [[../docs/pipeline-overview]]
- [[../logs/decisions-log]]
- [[../logs/test-results-2026-05-28]]
- [[../agents/orchestrator]]
- [[../agents/knowledge-builder]]
- [[../agents/dsp-research]]
- [[../agents/cpp-dev]]
- [[../agents/test-qa]]
- [[../agents/docs]]
