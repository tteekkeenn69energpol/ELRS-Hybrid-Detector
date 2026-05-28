---
tags: [external, KB-extra, group-5, github, cfar, matlab, ca-cfar, sfnd]
created: 2026-05-28
type: github
stage: 1
source_url: https://github.com/sunsided/SFND_Radar_2D_CFAR
status: done
language: MATLAB
---

# sunsided/SFND_Radar_2D_CFAR

## Опис
2D **CA-CFAR** на FMCW radar — найчистіша референс-реалізація з docs (db2pow / pow2db явно показано).

## Параметри
- Training: **8 range × 8 Doppler**
- Guard: **4 range × 4 Doppler**
- Threshold offset: **8 dB**

## Алгоритм (детально)
1. Sliding CUT по Range Doppler Map
2. Sum training cells (з dB → linear)
3. Average
4. Convert back to dB
5. Add offset threshold
6. Compare cell vs threshold

## License
Не вказано

## Релевантність
- **Найкраща канонічна референс-реалізація** для портування до нашого C++ block
- Чіткий код show-how для **dB↔linear arithmetic** (важливо: average **у linear**, threshold **у dB**) — не банально
- Параметри 8/8 + 4/4 + 8 dB — гарна **стартова точка** для прототипу

## Посилання
- [[ext-github-cfar-26]], [[ext-github-cfar-28]], [[ext-github-cfar-29]], [[ext-github-cfar-30]]
- [[08-stage1-oscfar-cpp]] — наш port target
- [[ext-cfar-theory-02]] — MATLAB API
