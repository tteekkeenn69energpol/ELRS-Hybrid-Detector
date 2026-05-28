---
tags: [knowledge-builder, tz, analysis, wigner-ville, hough, offline-verifier]
created: 2026-05-28
type: analysis
stage: 3-offline
status: approved-with-modifications
score: 6.5/10
drive_id: 1olHyhAxaPrlSxIj-iR7LiDm9zeFqoZ-E0pamq1NOOTU
source: 04_tz3_wigner_hough_transform.md
---

# ТЗ №3: Wigner-Hough Transform для детекції чирпів

## Вердикт
6.5/10 — APPROVED з суттєвими модифікаціями. Теоретично потужний метод (WVD дає оптимальну TF-локалізацію для лінійних чирпів), але **критично складний для реалізації в реальному часі**.
**Рекомендація**: використовувати як **офлайн-аналітичний інструмент / верифікатор** для інших методів, а не як основний детектор.

## Сильні сторони
- WVD: оптимальна часо-частотна локалізація для лінійних чирпів
- Hough накопичення енергії покращує детекцію при низькому SNR
- Пряма оцінка chirp rate → SF/BW без перебору
- Універсальний (будь-які лінійні чирпи)

## Критичні проблеми
1. **Складність**: O(N²) WVD + класичний Hough O(N_pixels × N_θ × N_ρ) ≈ 100M+ ops/buffer. На GPU 30-80 ms (на межі вимоги).
2. **Cross-term interference**: 8 однакових up-chirps дають перехресні члени → фантомні лінії в TF-площині.
3. **Немає GPU-бібліотек**: PyWVD/tftb тільки CPU. Потрібні custom CUDA kernels (+2-4 тижні розробки).
4. **Чутливість до CFO/STO**: потрібна попередня корекція (+5-10 ms латентності).

## Рекомендована архітектура v1.1
```
I/Q (50-100 ms)
 → Coarse Pre-Proc (CFO, downsample to 256 kS/s, windowing)
 → Pseudo-WVD (GPU, N=512-1024, window 64-128)
 → Focused Hough (тільки навколо очікуваних chirp rates, adaptive bins, early termination)
 → Output: SF/BW/chirp_rate (для верифікації)
```

## Залежності
- Верифікатор для [[02-tz1-dechirp-mf]]
- Альтернатива до [[05-tz4-nelora]] для офлайн аналізу
- Координується через [[06-tz5-hybrid-pipeline]]
