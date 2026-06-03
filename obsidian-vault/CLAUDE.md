# CLAUDE.md — Спільні правила для всіх агентів

## Проєкт
Розробка пристрою (ELRS-based) з використанням мультиагентної системи Claude Code.

## Поточний фокус — Stage 2

**Stage 2 — Blind Parameter Estimator** (Python/CuPy, DWT + CWT/SST).

Stage 2 отримує PMT trigger від Stage 1 (~1–5% потоку) і визначає **SF** (7–12) та **BW** (203/406/812/1625 kHz) для буфера IQ 50–100 мс. Архітектура: DWT pre-screen → CWT refinement → Confidence gate → PDU у Stage 3.

План: [[docs/stage2-plan]] · ТЗ: [[research/stage2-tz-dwt-cwt]] · Pipeline: [[docs/pipeline-overview]]

### Критерії готовності Stage 2
- [ ] `src/stage2/blind_estimator.py` + `gr_blind_estimator.py` реалізовані
- [ ] SF accuracy ≥ 85% @ SNR ≥ -10 dB
- [ ] BW accuracy ≥ 80% @ SNR ≥ -12 dB
- [ ] SF+BW pair ≥ 78% @ SNR = -14 dB
- [ ] Latency ≤ 25 мс на буфер 50 мс (RTX 3070)
- [ ] Test/QA PASS verdict
- [ ] Obsidian vault оновлений
- [ ] Git коміт зі Stage 2 результатами

### Завершені етапи
- ✅ **Stage 1 — 2D OS-CFAR standalone** (Pfa=0/10.5M, Throughput=86.27 MS/s parallel, Pd=1.0 @ SNR=−6dB). Коміти: 308f60d, e3668ec, 62c54cc, 1056283.

## Структура репозиторію

```
/device-project/
  CLAUDE.md          ← цей файл, спільні правила
  PROGRESS.md        ← checklist кроків (головний документ)
  /agents/           ← системні промпти кожного агента
  /obsidian/         ← Obsidian vault (синхронізується)
  /src/              ← код та прототипи
  /docs/             ← технічна документація
  /tests/            ← тести та бенчмарки
```

## Золоті правила

1. **Один крок = один агент.** Оркестратор читає `PROGRESS.md` і призначає лише одного виконавця за раз.
2. **Артефакт = done.** Крок вважається виконаним тільки якщо є файл у `/src/` або коміт у GitHub.
3. **Test блокує.** Без підтвердження від Test/QA агента — оркестратор не відкриває наступний крок. Жорстке правило.
4. **Docs після кожного кроку.** Docs-агент синхронізує Obsidian і робить коміт після кожного завершеного кроку.
5. **Не виконувати поза своєю роллю.** Кожен агент працює строго у своїй зоні відповідальності.

## Критерії готовності Stage 1 (закрито 2026-05-28)

- [x] C++ реалізація 2D OS-CFAR завершена (`cfar2d.hpp` / `cfar2d.cpp`)
- [x] Throughput ≥ 80 MS/s — **86.27 MS/s** (parallel, 20 threads)
- [x] Pfa ≤ 1% на синтетичних даних — **0 / 10.5M cells**
- [x] Тести пройдені та задокументовані
- [x] Obsidian vault оновлений
- [x] GitHub: коміти `308f60d` (C), `e3668ec` (T), `62c54cc` (D), `1056283` (KB-extra)

## Shared context

Всі агенти читають:
- `CLAUDE.md` (цей файл) — правила
- `PROGRESS.md` — поточний стан
- `/obsidian/` — база знань та рішення
