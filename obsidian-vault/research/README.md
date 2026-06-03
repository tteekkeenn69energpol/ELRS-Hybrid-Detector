# ELRS HYBRID DETECTOR
**Multi-Stage Cascaded Detection & Jamming System**  
Травень 2026 | Конфіденційно

---

## Структура файлів

```
elrs_docs/
├── README.md                          ← цей файл
│
├── presentation/
│   └── ELRS_Presentation_Slides.md   ← всі слайди презентації (текст)
│
├── TZ/
│   ├── TZ_01_Dechirping_Matched_Filter_Bank.md
│   ├── TZ_02_DWT_CWT_Blind_Parameter_Estimator.md
│   ├── TZ_03_Wigner_Hough_Transform.md
│   ├── TZ_04_STFT_OS_CFAR_Pipeline.md
│   └── TZ_05_Hybrid_MultiStage_Pipeline.md
│
└── integration/
    ├── TZ_06_GNU_Radio_Integration.md
    ├── OOT_Module_Setup_Instructions.md
    └── Flowgraph_elrs_full_detector.md
```

---

## TZ/ — Технічні завдання

| Файл | Stage | Метод | Пріоритет |
|------|-------|-------|-----------|
| TZ_01_Dechirping_Matched_Filter_Bank.md | Stage 3 | Dechirping + MF | Високий |
| TZ_02_DWT_CWT_Blind_Parameter_Estimator.md | Stage 2 | DWT + CWT/SST | Високий |
| TZ_03_Wigner_Hough_Transform.md | Stage 3 (альт.) | WHT | Середньо-Високий |
| TZ_04_STFT_OS_CFAR_Pipeline.md | Stage 1 | STFT + 2D OS-CFAR | Високий |
| TZ_05_Hybrid_MultiStage_Pipeline.md | Stage 0–5 | Повний pipeline | Високий |

## integration/ — Інтеграція з GNU Radio

| Файл | Опис |
|------|------|
| TZ_06_GNU_Radio_Integration.md | ТЗ на інтеграцію, архітектура OOT-модуля, блоки |
| OOT_Module_Setup_Instructions.md | Покрокова інструкція gr_modtool, CMake, компіляція |
| Flowgraph_elrs_full_detector.md | Опис flowgraph: блоки, з'єднання, параметри |
