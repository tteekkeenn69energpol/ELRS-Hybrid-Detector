# Stage 2 — Blind Parameter Estimator
## Повний план розробки

---
tags: [stage-2, plan, dwt, cwt, blind-estimator, dechirp, matched-filter]
created: 2026-05-29
status: ready-to-start
agent: orchestrator
---

## Контекст

Stage 1 (2D OS-CFAR) закрито ✅ — Pfa=0/10.5M, Throughput=86.27 MS/s.

Stage 2 отримує **PMT trigger** від Stage 1 (~1–5% потоку) і визначає параметри сигналу:
- **SF** (Spreading Factor): 7–12
- **BW** (Bandwidth): 203 / 406 / 812 / 1625 kHz
- **Confidence** score для Stage 3

Без Stage 2 Stage 3 (Dechirp + Matched Filter) не знає які параметри використовувати.

---

## Архітектура Stage 2

```
Stage 1 (OS-CFAR)
    ↓ PMT message {time, freq, power}
    ↓ (~1-5% потоку)
┌─────────────────────────────────────────┐
│         Stage 2: Blind Estimator        │
│                                         │
│  IQ buffer (50-100ms навколо тригера)   │
│         ↓                               │
│  [2a] DWT pre-screen                    │
│   → top-2 кандидати SF                  │
│         ↓                               │
│  [2b] CWT/SST refinement (Morlet)       │
│   → точний BW                           │
│         ↓                               │
│  [2c] Confidence gate                   │
│   → якщо < 0.4: відкинути              │
│   → якщо > 0.7: прямо в Stage 3        │
│   → якщо 0.4–0.7: Stage 4 (Neural)     │
└─────────────────────────────────────────┘
    ↓ PDU: {sf, bw, confidence, t_offset}
Stage 3 (Dechirp + Matched Filter)
```

---

## Цільові метрики Stage 2

| Метрика | Ціль | Блокує |
|---------|------|--------|
| SF accuracy | ≥ 85% @ SNR ≥ -10 dB | ✅ ТАК |
| BW accuracy | ≥ 80% @ SNR ≥ -12 dB | ✅ ТАК |
| SF+BW pair | ≥ 78% @ SNR = -14 dB | ✅ ТАК |
| Latency | ≤ 25 мс на буфер 50 мс | ✅ ТАК |
| False trigger rate | ≤ 5% | ⚠️ Інфо |

---

## Розподіл задач по агентах

### 🔬 DSP Research — R2-1..R2-5

**Задача:** Специфікація алгоритмів DWT+CWT для ELRS сигналів

**R2-1 — Специфікація DWT для SF estimation**
- Вибір вейвлету: Daubechies (db4/db8) vs Symlet (sym5/sym8)
- Рівень розкладання: оптимальний для SF7–12
- Метод аналізу: автокореляція детальних коефіцієнтів
- Порогові значення для кожного SF
- Обґрунтування вибору з посиланнями на `research/03-tz2-dwt-cwt.md`
- Артефакт: `/obsidian/docs/stage2-dwt-spec.md`

**R2-2 — Специфікація CWT для BW estimation**
- Вибір вейвлету: Morlet vs Morse
- Synchrosqueezing (SST): чи потрібен для ELRS BW?
- Mapping: scale → BW для кожного з 4 значень (203/406/812/1625 kHz)
- Точність при різних SNR
- Артефакт: розширення `/obsidian/docs/stage2-dwt-spec.md`

**R2-3 — Confidence gate специфікація**
- Формула combined score: DWT score + CWT energy
- Пороги: 0.4 (відкинути) / 0.7 (прямо в Stage 3) / між — Neural
- Калібрування на синтетиці SF7–12 × 4 BW
- Артефакт: таблиця порогів у `stage2-dwt-spec.md`

**R2-4 — Інтерфейс для Python Dev**
```python
# Очікуваний інтерфейс
class ELRS_BlindParameterEstimator:
    def __init__(self, samp_rate: float, wavelet: str = 'sym5')
    def estimate(self, iq_buffer: np.ndarray) -> dict:
        # Returns: {sf, bw, confidence, method, t_offset_samples}
```

**R2-5 — Самопідтвердження**
- Перевірити узгодженість з `research/03-tz2-dwt-cwt.md` та `TZ_02_DWT_CWT_Blind_Parameter_Estimator.md`
- Status: draft → approved
- Повідомити Оркестратора: "R2-1..R2-5 done"

---

### 🐍 Python Dev — C2-1..C2-6

**Задача:** Реалізація `blind_estimator.py` на Python/CuPy

**C2-1 — Середовище та залежності**
```bash
pip install pywt cupy-cuda12x ssqueezepy scipy numpy
```
- Перевірити CuPy + CUDA сумісність на RTX 3070
- Створити `/src/stage2/requirements.txt`
- Артефакт: `requirements.txt`

**C2-2 — DWT SF Estimator**
- Реалізувати `dwt_sf_estimation(iq: np.ndarray) → {sf, score}`
- Багаторівневий DWT (pywt.wavedec)
- Автокореляція детальних коефіцієнтів
- Пошук піку біля `symbol_len = 2**sf`
- Без GPU на цьому кроці (DWT швидкий на CPU)
- Артефакт: `/src/stage2/dwt_estimator.py`

**C2-3 — CWT BW Estimator**
- Реалізувати `cwt_bw_estimation(iq: cp.ndarray) → {bw, energy}`
- Morlet wavelet через ssqueezepy або scipy.signal.cwt
- CuPy для GPU прискорення
- Mapping scale → BW (калібрувальна таблиця)
- Артефакт: `/src/stage2/cwt_estimator.py`

**C2-4 — Головний модуль ELRS_BlindParameterEstimator**
- Об'єднати DWT + CWT
- Confidence gate логіка
- PMT message parser (від Stage 1)
- PDU output для Stage 3
- Точно за інтерфейсом зі специфікації R2-4
- Артефакт: `/src/stage2/blind_estimator.py`

**C2-5 — GNU Radio Python Block**
```python
class Blind_Parameter_Estimator(gr.sync_block):
    # Wrapps blind_estimator.py як GNU Radio блок
    # Input: complex64 stream
    # Output: PDU message {sf, bw, confidence}
```
- Артефакт: `/src/stage2/gr_blind_estimator.py`

**C2-6 — Benchmark вбудований**
- Виміряти latency на буфері 50 мс
- Ціль: ≤ 25 мс на RTX 3070
- Артефакт: `/src/stage2/bench_stage2.py`

---

### 🧪 Test/QA — T2-1..T2-7 ← БЛОКУЮЧИЙ

**Задача:** Валідація Stage 2

**T2-1 — Синтетичний датасет**
- Всі 24 комбінації SF7–12 × BW (203/406/812/1625 kHz)
- SNR sweep: -14 → +10 дБ, крок 2 дБ
- N=500 сигналів на комбінацію = 12,000 тестів
- Артефакт: `/tests/stage2/synth_dataset.py`

**T2-2 — SF accuracy test** ← БЛОКУЮЧИЙ
- Ціль: ≥ 85% при SNR ≥ -10 дБ
- Confusion matrix SF7 vs SF8 vs ... vs SF12
- Артефакт: `/tests/stage2/test_sf_accuracy.py`

**T2-3 — BW accuracy test** ← БЛОКУЮЧИЙ
- Ціль: ≥ 80% при SNR ≥ -12 дБ
- Confusion matrix 4 класи BW
- Артефакт: `/tests/stage2/test_bw_accuracy.py`

**T2-4 — Combined SF+BW accuracy** ← БЛОКУЮЧИЙ
- Ціль: ≥ 78% @ SNR = -14 дБ
- Точна пара (SF, BW) разом
- Артефакт: результати в `test-results-stage2.md`

**T2-5 — Latency benchmark** ← БЛОКУЮЧИЙ
- Незалежний від bench_stage2.py
- 50 мс буфер, 10 повторень, медіана
- Ціль: ≤ 25 мс
- Артефакт: latency table в `test-results-stage2.md`

**T2-6 — Confidence gate test**
- Перевірити що gate правильно відфільтровує низькоякісні результати
- False trigger rate ≤ 5%
- Артефакт: gate stats в `test-results-stage2.md`

**T2-7 — Вердикт**
```
✅ PASS — SF≥85%, BW≥80%, pair≥78%, latency≤25ms
❌ FAIL — який критерій провалено + аналіз
```
- Артефакт: `/tests/stage2/test-results-stage2.md` + plots

---

### 📚 Docs — D2-1..D2-4

**Задача:** Синхронізація після Stage 2

**D2-1 — Оновити Obsidian**
- `/obsidian/docs/stage2-dwt-spec.md` — фінальна специфікація
- `/obsidian/00-overview/project-overview.md` — оновити статус Stage 2
- `/obsidian/logs/decisions-log.md` — рішення Stage 2 (вейвлет, пороги, gate)
- `/obsidian/logs/progress-snapshots/2026-05-XX-stage2-done.md`

**D2-2 — Оновити PROGRESS.md**
- R2/C2/T2/D2 кроки → [x]
- Додати Stage 2 DoD чекліст
- Лог рішень

**D2-3 — Оновити README.md**
- Додати Stage 2 результати
- Як запустити Stage 2 тести

**D2-4 — Git коміт**
```
"docs: D2-1..D2-4 sync after Stage 2 (SF≥X%, BW≥Y%, PASS)"
```

---

## Покроковий цикл Stage 2

```
Крок R2 (DSP Research)
    ↓ stage2-dwt-spec.md (approved)
Крок C2 (Python Dev)
    ↓ blind_estimator.py + gr_blind_estimator.py
Крок T2 (Test/QA) ← БЛОКУЮЧИЙ
    ↓ PASS: SF≥85%, BW≥80%, latency≤25ms
Крок D2 (Docs)
    ↓ vault синхронізований, git коміт
Stage 2 CLOSED → Stage 3
```

---

## Що потрібно завантажити до старту

### Knowledge Builder (KB-stage2) — одноразово

Завантажити та розпарсити в `research/`:

**З Google Drive:**
- Папка 1 (`1AjaKtXUvsCoKfdeBpYp8gUn3iTs5JpCc`):
  - `Доппитання` — 45 питань для DWT/CWT аналізу
  - `Section 1: Architecture & Principles` — відповіді NotebookLM

- Папка 2 (`1YKR02MsWSyqnjr2D3bTtOO6IYHScgAsj`):
  - `Документ без назви` — математика dechirping/ортогональність
  - `"LoRa CSS dechirping..."` — дослідницькі запити

**Локальні .md файли (вже завантажені):**
- `TZ_02_DWT_CWT_Blind_Parameter_Estimator.md` → `research/stage2-tz-dwt-cwt.md`
- `TZ_01_Dechirping_Matched_Filter_Bank.md` → `research/stage2-tz-dechirp-mf.md`
- `TZ_03_Wigner_Hough_Transform.md` → `research/stage2-tz-wigner-hough.md`
- `TZ_05_Hybrid_MultiStage_Pipeline.md` → `research/stage2-tz-hybrid-pipeline.md`
- `TZ_06_GNU_Radio_Integration.md` → `research/stage2-tz-gnuradio.md`
- `OOT_Module_Setup_Instructions.md` → `research/stage2-oot-setup.md`
- `Flowgraph_elrs_full_detector.md` → `research/stage2-flowgraph.md`
- `ELRS_Presentation_Slides.md` → `research/stage2-presentation.md`

**Зовнішні джерела (вже є у vault):**
- `research/03-tz2-dwt-cwt.md`
- `research/09-stage2-blind-estimator-py.md`
- `research/ext-lora-detection-09.md`
- `research/ext-cfar-theory-*.md`

---

## Оновлення CLAUDE.md для Stage 2

```markdown
## Поточний фокус — Stage 2

**Stage 2 — Blind Parameter Estimator** (Python/CuPy)

Критерії готовності Stage 2:
- [ ] blind_estimator.py реалізовано
- [ ] SF accuracy ≥ 85% @ SNR ≥ -10 dB
- [ ] BW accuracy ≥ 80% @ SNR ≥ -12 dB
- [ ] SF+BW pair ≥ 78% @ SNR = -14 dB
- [ ] Latency ≤ 25 мс на буфер 50 мс
- [ ] GNU Radio Python Block готовий
- [ ] Тести пройдені та задокументовані
- [ ] Obsidian vault оновлений
- [ ] Git коміт
```

---

## Зміни в промптах агентів для Stage 2

### DSP Research
Додати в початок:
```
Stage 2 контекст: твоя задача — специфікація DWT+CWT алгоритмів.
Читай: /obsidian/research/stage2-tz-dwt-cwt.md (головний ТЗ),
       /obsidian/research/03-tz2-dwt-cwt.md (аналіз),
       /obsidian/research/09-stage2-blind-estimator-py.md (код референс).
Артефакт: /obsidian/docs/stage2-dwt-spec.md
```

### Python Dev (новий агент замість C++ Dev для Stage 2)
```
Ти — Python/CuPy розробник для Stage 2.
Читай spec: /obsidian/docs/stage2-dwt-spec.md
Реалізуй: /src/stage2/blind_estimator.py
Залежності: pywt, cupy, ssqueezepy, scipy
НЕ писати тести (Test/QA), НЕ писати документацію (Docs)
```

### Test/QA
Додати:
```
Stage 2 блокуючі метрики:
- SF accuracy ≥ 85% @ SNR ≥ -10 dB
- BW accuracy ≥ 80% @ SNR ≥ -12 dB
- SF+BW pair ≥ 78% @ SNR = -14 dB
- Latency ≤ 25 мс
Синтетика: 24 комбінації SF×BW, SNR sweep -14→+10 dB
```

---

## PROGRESS.md — Секція Stage 2

```markdown
## Фаза 2 — Stage 2: Blind Parameter Estimator

### Крок 0 — Knowledge Builder (KB-stage2)
- [ ] **KB-S2-1** Завантажити матеріали з Google Drive папок
- [ ] **KB-S2-2** Розпарсити 8 локальних .md файлів → research/
- [ ] **KB-S2-3** Створити нотатки з ключовими алгоритмами
- [ ] **KB-S2-4** Оновити sources.md

### Крок 1 — Специфікація (DSP Research)
- [ ] **R2-1** DWT специфікація (вейвлет, рівні, SF mapping)
- [ ] **R2-2** CWT специфікація (Morlet, SST, BW mapping)
- [ ] **R2-3** Confidence gate пороги
- [ ] **R2-4** Python інтерфейс визначений
- [ ] **R2-5** Специфікація approved → stage2-dwt-spec.md

### Крок 2 — Реалізація (Python Dev)
- [ ] **C2-1** Середовище та залежності
- [ ] **C2-2** DWT SF Estimator (dwt_estimator.py)
- [ ] **C2-3** CWT BW Estimator (cwt_estimator.py)
- [ ] **C2-4** Головний модуль (blind_estimator.py)
- [ ] **C2-5** GNU Radio Python Block (gr_blind_estimator.py)
- [ ] **C2-6** Benchmark (≤ 25 мс)

### Крок 3 — Тестування (Test/QA) ← БЛОКУЮЧИЙ
- [ ] **T2-1** Синтетичний датасет (12,000 тестів)
- [ ] **T2-2** SF accuracy ≥ 85% ← блокує
- [ ] **T2-3** BW accuracy ≥ 80% ← блокує
- [ ] **T2-4** SF+BW pair ≥ 78% ← блокує
- [ ] **T2-5** Latency ≤ 25 мс ← блокує
- [ ] **T2-6** Confidence gate test
- [ ] **T2-7** ✅ Вердикт PASS/FAIL

### Крок 4 — Документація (Docs)
- [ ] **D2-1** Оновити Obsidian (spec, decisions, overview)
- [ ] **D2-2** Оновити PROGRESS.md
- [ ] **D2-3** Оновити README.md
- [ ] **D2-4** Git коміт "docs: Stage 2 sync"
```

---

## Посилання

- [[../docs/stage2-dwt-spec]] ← заповнить DSP Research
- [[../research/stage2-tz-dwt-cwt]] ← головний ТЗ
- [[../research/03-tz2-dwt-cwt]] ← аналіз алгоритму
- [[../research/09-stage2-blind-estimator-py]] ← код референс
- [[../docs/pipeline-overview]] ← загальна архітектура
- [[../00-overview/project-overview]] ← поточний стан проєкту
- [[../logs/decisions-log]] ← лог рішень
