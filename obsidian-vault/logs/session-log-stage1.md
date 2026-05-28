# ELRS Hybrid Detector — Лог сесії розробки Stage 1
**Дата:** 2026-05-28  
**Тривалість:** ~1 робоча сесія  
**Результат:** Stage 1 (2D OS-CFAR) — ✅ PASS

---

## Контекст

Розробка пристрою ELRS Hybrid Detector — каскадного пайплайну виявлення ELRS FHSS сигналів у ISM 915 MHz. Система будується за допомогою **6 Claude агентів** через Claude Code CLI.

---

## Що було зроблено в цій сесії

### 1. Створення Obsidian Vault

Побудовано структуру vault для проєкту:

```
/device-project/
  CLAUDE.md          ← спільні правила для всіх агентів
  PROGRESS.md        ← checklist кроків
  /agents/           ← системні промпти агентів
  /obsidian/         ← vault
  /src/              ← код
  /tests/            ← тести
  /docs/             ← документація
```

Створено системні промпти для 6 агентів:
- **Оркестратор** — читає PROGRESS.md, призначає кроки, не виконує сам
- **Knowledge Builder** — одноразовий, парсить матеріали, ініціалізує vault
- **DSP Research** — алгоритми, специфікації, параметри
- **C++ Dev** — реалізація коду
- **Test/QA** — блокуючий агент, валідує кроки
- **Docs** — пам'ять системи, синхронізація

Додано **пам'ять між сесіями** — кожен агент читає `PROGRESS.md` + `logs/` на початку кожної сесії.

---

### 2. Завантаження бази знань (Knowledge Builder)

**Джерела що були завантажені:**

| Папка | Кількість | Що |
|-------|-----------|-----|
| Google Drive папка 1 (Roles & Pipeline) | 17 документів | ТЗ, аналізи, код, ролі |
| Google Drive папка 2 (CFAR) | 3 документи | Dataset CFAR, CUDA pipeline, питання |
| Google Drive папка 3 (Detector статті) | 6 PDF | Academic papers |
| GRCon25 | 2 PDF | ELRS GNU Radio реалізація |
| Локальні матеріали | 1 файл | OS-CFAR теорія, ТЗ, код |
| GitHub репо | 2 | lora-net, expresslrs |

**Всього:** 29+ файлів у `research/`

**Ключові документи:**
- `dataset-cfar.md` — повна математика OS-CFAR (5 розділів)
- `pipeline-overview.md` — каскадна архітектура Stage 1→2→3→4
- `20-grcon25-elrs-gnuradio-paper.md` — перша відкрита реалізація ELRS у GNU Radio (FAU)
- `21-os-cfar-realtime-impl.md` — Georgia Tech/AFRL rank-only підхід

---

### 3. Фаза R: DSP Research — Специфікація OS-CFAR

**Агент:** DSP Research  
**Результат:** `cfar-spec.md` (status=approved)

**Визначені параметри:**

| Параметр | Значення | Обґрунтування |
|----------|----------|---------------|
| `N_guard_f` | 4 | Захист від self-masking чирпу |
| `N_guard_t` | 2 | 2 кадри для ELRS преамбули |
| `N_ref_f` | 16 | Стабільна оцінка ISM-шуму |
| `N_ref_t` | 8 | Баланс throughput vs точність |
| `N_train_total` | 816 | 41×21 − 9×5 |
| `k` | 612 | rank_percent=0.75 × 816 |
| `threshold_db` | 12.5 dB | α=17.78, Pfa≈3.55e-11 |
| `min_snr_db` | 7.0 dB | Hard floor |

**C++ інтерфейс:**
```cpp
struct Detection { int t_idx; int f_idx; float power_db; float snr_db; };
struct CFAR2DParams { N_ref_f=16, N_ref_t=8, N_guard_f=4, N_guard_t=2,
                      rank_percent=0.75f, threshold_db=12.5f, min_snr_db=7.0f };
class CFAR2D {
    explicit CFAR2D(const CFAR2DParams& p);
    std::vector<Detection> process(const float* power, int rows, int cols);
    double throughput_ms() const noexcept;
    void set_params(const CFAR2DParams& p);
};
```

---

### 4. Фаза C: C++ Dev — Реалізація

**Агент:** C++ Dev  
**Коміт:** `308f60d`  
**Файли:** `src/cfar2d.hpp`, `src/cfar2d.cpp`, `src/CMakeLists.txt`, `src/bench_main.cpp`

**Ключова оптимізація:**

Замість `std::nth_element` для кожної з 1M+ комірок → **SIMD count-rank pre-filter**:

```
Детекція ⟺ X(k) < CUT/α ⟺ count(refs < CUT/α) > k
```

AVX2 `count_lt_simd` рахує кількість reference cells нижче порогу за O(N/8) з unrolled 32-wide loop. `nth_element` викликається тільки для ~0.01% комірок що пройшли CFAR.

**Результати benchmark:**

| Mode | Throughput |
|------|-----------|
| Single-thread | 14.10 MS/s |
| Parallel (20 threads, row-stripe tiling) | **89.96 MS/s** ✅ |

Компіляція: `g++ -O3 -mavx2 -march=native -Wall -Wextra -Wpedantic` — чиста, без warnings.

---

### 5. Фаза T: Test/QA — Валідація

**Агент:** Test/QA  
**Коміт:** `e3668ec`  
**Вердикт:** ✅ **PASS**

**Методологія:**
- C ABI wrapper (`cfar2d_c.cpp`) → Python ctypes binding (`cfar2d_py.py`)
- Синтетичні дані: AWGN (Rayleigh) + ELRS chirp преамбула (8 up + 2 SYNC + 2.25 down)
- STFT: fft=2048, hop=512 (75% overlap), Blackman-Harris, fs=30.72 MS/s
- Monte-Carlo Pfa: 10,485,760 комірок

**Результати:**

| Метрика | Результат | Ціль | Статус |
|---------|-----------|------|--------|
| Pfa (MC) | 0 / 10,485,760 | ≤ 1% | ✅ |
| Pfa (analytic) | 3.555e-11 | — | ✅ узгоджено |
| MC↔analytic | 8dB: 1.14×, 10dB: 1.44× | ±20% | ✅ |
| Throughput (parallel) | 86.27 MS/s | ≥ 80 MS/s | ✅ |
| Pd @ SNR=−6 dB | 1.000 (200/200) | ≥ 0.92 | ✅ |

**Артефакти:** `tests/test-results.{md,json,png}`, `tests/run.sh`, відтворювані скрипти.

---

### 6. Фаза D: Docs — Синхронізація

**Агент:** Docs  
**Коміт:** `62c54cc`  
**Файли створено:**

| Файл | Призначення |
|------|------------|
| `00-overview/project-overview.md` | Призначення, метрики Stage 1, roadmap |
| `00-overview/architecture.md` | 6-agent система, hand-off flow, ASCII pipeline |
| `logs/decisions-log.md` | P-01..P-10 процесні + A-01..A-08 алгоритмічні рішення |
| `logs/progress-snapshots/2026-05-28-stage1-done.md` | Snapshot PROGRESS.md |
| `README.md` | Repo root: build, тести, результати, roadmap |
| `PROGRESS.md` | Оновлено: D-1..D-4 [x], Stage 1 DoD закрито |

**Граф знань зв'язаний:**
```
[[cfar-spec]] ↔ [[test-results-2026-05-28]] ↔ [[08-stage1-oscfar-cpp]]
      ↕                    ↕                          ↕
[[decisions-log]] ↔ [[project-overview]] ↔ [[architecture]]
```

---

## Git лог Stage 1

```
62c54cc  docs: D-1..D-4 sync after Stage 1 (Pfa=0, Thrpt=86 MS/s, PASS)
e3668ec  T-1..T-6: Test/QA Stage-1 2D OS-CFAR — VERDICT: PASS
308f60d  C-1..C-5: 2D OS-CFAR (k=612, rank=0.75), AVX2, bench 89.96 MS/s
```

---

## Підсумок Stage 1

```
Фаза 0 (KB)   ████████████ 100%  ✅  29+ документів розпарсено
Крок 1 (R)    ████████████ 100%  ✅  cfar-spec.md approved
Крок 2 (C)    ████████████ 100%  ✅  89.96 MS/s, commit 308f60d
Крок 3 (T)    ████████████ 100%  ✅  PASS, Pfa=0/10.5M, commit e3668ec
Крок 4 (D)    ████████████ 100%  ✅  README + vault синхронізовано, commit 62c54cc
```

---

## Наступний крок — Stage 2

**Blind Parameter Estimator** (DWT/CWT, Python/CuPy)

Документи готові:
- `research/03-tz2-dwt-cwt.md`
- `research/09-stage2-blind-estimator-py.md`
- `docs/pipeline-overview.md` §Stage 2

Агент: **DSP Research** → специфікація параметрів DWT/CWT  
Потім: **C++ Dev / Python Dev** → реалізація  
Gate: **Test/QA** → валідація

---

## Нотатки по системі агентів

### Що працювало добре
- Оркестратор чітко розподіляв задачі і не виконував їх сам
- Test/QA gate не дав перейти далі без підтвердження метрик
- Knowledge Builder одноразово завантажив всю базу знань
- Пам'ять між сесіями через файли (`PROGRESS.md` + `logs/`)

### Важливі уроки
- `gdown --folder` потребує окремого дозволу на кожну папку Drive
- `pymupdf` (`fitz`) треба встановлювати з `--break-system-packages`
- C++ benchmark першої версії: 0.22 MS/s → після SIMD оптимізації: 89.96 MS/s (400×!)
- ctypes binding до C++ через C ABI wrapper — надійніший підхід ніж pybind11 для тестів

### Питання до вирішення у Stage 2+
- Реальні IQ-записи з SPECTRAN V6 (поки тільки синтетика)
- GNU Radio OOT блок (обгортка навколо `cfar2d.cpp`)
- CUDA міграція для 245 MS/s (повний bandwidth SPECTRAN V6 500XA-6)
- 45 відкритих дослідницьких питань → `research/18-research-questions.md`
