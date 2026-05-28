# PROGRESS.md — Checklist кроків

> Головний документ системи. Оркестратор читає його перед кожним призначенням.

## Статуси
- `[ ]` — не розпочато
- `[~]` — в процесі
- `[x]` — завершено і підтверджено Test/QA

---

## Фаза 0 — Одноразова ініціалізація (Knowledge Builder)

- [x] **KB-1** Запустити Knowledge Builder агента
- [x] **KB-2** Розпарсити джерела знань (19 Google Drive docs замість pptx — scope-shift, артефакт у `/research/`)
- [x] **KB-3** Створити структуру Obsidian vault (`research/`, `docs/`, `00-overview/`, `logs/`)
- [x] **KB-4** `CLAUDE.md` присутній (узгоджено з існуючим — генерація не потрібна)
- [x] **KB-5** Системні промпти агентів присутні в `/agents/` (6 файлів)
- [x] **KB-6** ✅ Knowledge Builder завершив роботу (більше не потрібен)

---

## Фаза 1 — Stage 1: 2D OS-CFAR standalone модуль

### Крок 1 — Специфікація алгоритму (DSP Research)
- [x] **R-1** Параметри: N_guard=4×2, N_ref=16×8, k=612 (rank=0.75)
- [x] **R-2** Pfa ≤ 1% (analytical + MC), Pd ≥ 0.92 @ SNR=−6dB (AWGN ціль)
- [x] **R-3** `cfar-spec.md` заповнено (status=approved)
- [x] **R-4** Самопідтверджено DSP Research, передано C++ Dev

### Крок 2 — Реалізація (C++ Dev)
- [x] **C-1** `cfar2d.hpp` + `cfar2d.cpp` (інтерфейс по специ, rank-only + nth_element)
- [x] **C-2** SIMD AVX2 (count-rank pre-filter, materialize X(k) лише на CUT-pass)
- [x] **C-3** Багатопотоковість через row-stripe tiling (1 instance per thread, спека §134)
- [x] **C-4** Throughput 89.96 MS/s (20 threads, parallel) ≥ 80 MS/s ✅ / 14.10 MS/s single
- [x] **C-5** Збережено в `/src/`, коміт `308f60d`

### Крок 3 — Тестування (Test/QA) ← БЛОКУЮЧИЙ
- [x] **T-1** Синтетичні дані: AWGN + chirp-сигнал (synth.py: STFT 2048/512/BH, ELRS preamble)
- [x] **T-2** Виміряти Pfa (MC=0 / 10.5M cells, analytic 3.55e-11 ≤ 1% ✅)
- [x] **T-3** ROC curve (7 SNRs × 11 thresholds, /tests/test-results.png)
- [x] **T-4** Throughput benchmark: 86.27 MS/s parallel (≥80 ✅), 13.53 MS/s single
- [x] **T-5** Збережено: `/tests/test-results.{md,json,png}` + `/obsidian-vault/logs/test-results-2026-05-28.md`
- [x] **T-6** ✅ Test/QA вердикт: **PASS** → Оркестратор відкриває Крок 4 (D-1)

### Крок 4 — Документація (Docs)
- [x] **D-1** Оновити Obsidian: spec, рішення, результати
- [x] **D-2** Оновити `PROGRESS.md`
- [x] **D-3** GitHub README + commit notes
- [x] **D-4** Синхронізація завершена

### ✅ Stage 1 — Definition of Done (per CLAUDE.md)
- [x] C++ реалізація 2D OS-CFAR завершена (`cfar2d.hpp` / `cfar2d.cpp`)
- [x] Throughput ≥ 80 MS/s — **86.27 MS/s** (parallel, 20 threads)
- [x] Pfa ≤ 1% на синтетичних даних — **0 / 10.5M cells** (analytic 3.55e-11)
- [x] Тести пройдені та задокументовані (`/tests/test-results.{md,json,png}`)
- [x] Obsidian vault оновлений (00-overview/, logs/, progress-snapshots/)
- [x] GitHub: коміти `308f60d` (C), `e3668ec` (T), D-4 (Docs sync)

---

## Фаза 2+ — (планується після Stage 1)

- [ ] Інтеграція з наступними компонентами пристрою
- [ ] ...

---

## Лог рішень

| Дата | Агент | Рішення |
|------|-------|---------|
| 2026-05-28 | Orchestrator | Призначено KB-1 → Knowledge Builder (старт Фази 0) |
| 2026-05-28 | Knowledge Builder | KB-2: 19 Google Drive docs розпарсено → `/research/` + `sources.md`; pipeline-overview.md створено |
| 2026-05-28 | Orchestrator | KB-1…KB-6 закрито (Фаза 0 done). Призначено R-1 → DSP Research |
| 2026-05-28 | DSP Research | R-1..R-4 done. Параметри: N_guard=4×2, N_ref=16×8, k=612, threshold_db=12.5, min_snr_db=7.0 |
| 2026-05-28 | Orchestrator | R-1..R-4 закрито (spec approved). Призначено C-1 → C++ Dev |
| 2026-05-28 | C++ Dev | C-1..C-5 done. Commit 308f60d. Throughput 89.96 MS/s (20 threads) / 14.10 MS/s single |
| 2026-05-28 | Orchestrator | C-1..C-5 закрито. Призначено T-1 → Test/QA (БЛОКУЮЧИЙ gate) |
| 2026-05-28 | Test/QA | T-1..T-6 done. **PASS**. Pfa MC=0/10.5M (analytic 3.55e-11) ≤ 1% ✅; Thrpt parallel=86.27 MS/s ≥ 80 ✅; Pd=1.0 @ SNR=−6dB. Артефакти у `/tests/` + `/obsidian-vault/logs/`. |
| 2026-05-28 | Orchestrator | T-6 PASS верифіковано (commit e3668ec, `/src/` недоторкано). Призначено D-1 → Docs (фінал Stage 1) |
| 2026-05-28 | Docs | D-1..D-4 done. Створено `00-overview/project-overview.md`, `00-overview/architecture.md`, `logs/decisions-log.md`, `logs/progress-snapshots/2026-05-28-stage1-done.md`, `/README.md`. Додано backlinks у `logs/test-results-2026-05-28.md` та `research/08-stage1-oscfar-cpp.md`. Stage 1 закрито. Чекліст `CLAUDE.md` звірено. |
| 2026-05-28 | Knowledge Builder | KB-extra: 40 ext links → research/ext-*.md (3 dup skipped) |
| 2026-05-28 | Docs | KB-extra sync + vault hygiene commit. Repo тепер повністю tracked. |
