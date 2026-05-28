Завдання KB-extra: завантаж та розпарси 40 посилань і створи нотатки в /obsidian-vault/research/

=== ГРУПИ ПОСИЛАНЬ ===

--- ГРУПА 1: CFAR теорія та алгоритми (8 посилань) ---
Для кожного: витягни назву, авторів, ключові ідеї, параметри, формули. Нотатка: research/ext-cfar-theory-XX.md

1. https://www.researchgate.net/publication/221021928_A_time_frequency_approach_to_CFAR_detection
2. https://www.mathworks.com/help/phased/ref/2dcfardetector.html
3. https://wirelesspi.com/adaptive-thresholding-in-radar-detection-using-constant-false-alarm-rate-cfar-techniques/
4. https://www.radartutorial.eu/01.basics/False%20Alarm%20Rate.en.html
5. https://www.emergentmind.com/topics/false-alarm-rate-far
6. https://www.globalscientificjournal.com/researchpaper/A_Novel_Approach_for_Accurate_Target_Detection_in_the_worst_Radar_Environments.pdf
7. https://etj.uotechnology.edu.iq/article_82064_83d418e5f4c4307a0b2f9ea5b54f989c.pdf
8. https://www.themoonlight.io/en/review/wilcoxon-nonparametric-cfar-scheme-for-ship-detection-in-sar-image

--- ГРУПА 2: LoRa / ELRS детекція (3 посилання) ---
Для кожного: витягни алгоритм детекції, параметри, результати. Нотатка: research/ext-lora-detection-XX.md

9.  https://www.researchgate.net/publication/366523206_LoRa_Preamble_Detection_with_Optimized_Thresholds
10. https://www.expresslrs.org/faq/
11. https://indico.cern.ch/event/268353/contributions/1606636/attachments/480140/664100/pres20130420.pdf

--- ГРУПА 3: Drone / RF detection papers (6 посилань) ---
Для кожного: архітектура системи, метрики, апаратура. Нотатка: research/ext-drone-rf-XX.md

12. https://www.researchgate.net/publication/376259721_RF_Drone_Detection_System_Based_on_a_Distributed_Sensor_Grid_With_Remote_Hardware-Accelerated_Signal_Processing
13. https://www.mdpi.com/2072-4292/16/13/2508
14. https://www.mdpi.com/2072-4292/12/8/1273
15. https://www.mdpi.com/2072-4292/13/8/1548
16. https://www.mdpi.com/2079-9292/14/7/1474
17. https://www.mdpi.com/2504-446X/10/2/117

--- ГРУПА 4: GPU CUDA оптимізація (8 посилань) ---
Для кожного: техніки оптимізації, shared memory, throughput. Нотатка: research/ext-cuda-gpu-XX.md

18. https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
19. https://developer.nvidia.com/nsight-compute
20. https://docs.nersc.gov/tools/performance/nvidiaproftools/
21. https://ajdillhoff.github.io/notes/profiling_cuda_applications/
22. https://developer.nvidia.com/blog/using-shared-memory-cuda-cc/
23. https://stackoverflow.com/questions/7656277/generalized-sliding-window-computation-on-the-gpu
24. https://numba.pydata.org/numba-doc/dev/cuda/kernels.html
25. https://docs.nvidia.com/pva/solutions/0.4.0/solutions-apis/group__PVA__OPERATOR__ALGORITHM__RADAR__CFAR.html

--- ГРУПА 5: GitHub репозиторії — CFAR реалізації (6 посилань) ---
Для кожного: мова, алгоритм, структура коду, ліцензія. Нотатка: research/ext-github-cfar-XX.md

26. https://github.com/BoJi07/Radar-target-generation-and-detection
27. https://github.com/KAdamek/GPU_Overlap-and-save_convolution
28. https://github.com/Swaroopainapurapu/Radar_2D_CFAR
29. https://github.com/nbarendes/SFND_Radar_2D_CIFAR_Process
30. https://github.com/stevenliu216/SFND_Radar_Target_Generation_and_Detection
31. https://github.com/sunsided/SFND_Radar_2D_CFAR

--- ГРУПА 6: GitHub репозиторії — GNU Radio / SDR (3 посилання) ---
Для кожного: блоки, інтерфейси, сумісність з нашим pipeline. Нотатка: research/ext-github-gnuradio-XX.md

32. https://github.com/gnuradio/gr-cuda
33. https://github.com/sandialabs/gr-fhss_utils
34. https://gist.github.com/juhasch/eeb05b25085fc644fcdd1002770486e8

--- ГРУПА 7: ML / AI для RF (4 посилання) ---
Для кожного: архітектура моделі, датасет, метрики. Нотатка: research/ext-ml-rf-XX.md

35. https://deepwave.ai/
36. https://pmc.ncbi.nlm.nih.gov/articles/PMC12074172/
37. https://pmc.ncbi.nlm.nih.gov/articles/PMC9413984/
38. https://pmc.ncbi.nlm.nih.gov/articles/PMC11914985/

--- ГРУПА 8: FMCW Radar / Signal Processing (2 посилання) ---
Для кожного: архітектура, CFAR застосування, DSP техніки. Нотатка: research/ext-fmcw-XX.md

39. https://www.researchgate.net/publication/389083744_Design_of_Reconfigurable_Radar_Signal_Processor_for_Frequency_Modulated_Continuous_Wave_Radar
40. https://repository.up.ac.za/server/api/core/bitstreams/2d45b988-018d-4f53-933e-f10e947dc1c8/content

=== ІНСТРУКЦІЯ ===

Для КОЖНОГО посилання:

1. Завантаж через wget або python3 requests:
   wget -q -O /tmp/kb_links/XX_назва.html "URL" 2>&1
   або для PDF:
   wget -q -O /tmp/kb_links/XX_назва.pdf "URL" 2>&1

2. Витягни текст:
   - HTML: python3 -c "from html.parser import HTMLParser; ..."
     або pip install --break-system-packages --user beautifulsoup4 && python3 -c "from bs4 import BeautifulSoup..."
   - PDF: python3 -c "import fitz; doc=fitz.open('file.pdf'); print('\n'.join(p.get_text() for p in doc))"
   - GitHub repo: читай README.md напряму
   
2б. Якщо посилання веде на PDF або містить PDF всередині сторінки:
    - Скачай PDF: wget -q -O /tmp/kb_links/XX_назва.pdf "URL_до_pdf"
    - Скопіюй у vault: cp /tmp/kb_links/XX_назва.pdf 
      /home/tekken/ELRS_Hybrid_Detector_Vault/ELRS_Hybrid_Detector_Vault/data/raw/pdf/
    - Витягни текст через fitz і створи нотатку як звичайно
    - У нотатці вкажи: local_pdf: data/raw/pdf/XX_назва.pdf

3. Створи нотатку /obsidian-vault/research/[назва].md:
---
tags: [external, KB-extra, група]
created: 2026-05-28
type: [paper/tool/github/docs]
stage: [1/2/3/4/all]
source_url: URL
status: done
---

# Назва

## Короткий зміст (2-3 речення)

## Ключові ідеї / алгоритми

## Релевантність до проєкту
- Stage X: що саме корисно

## Посилання
- [[суміжний файл у vault]]

4. Якщо посилання недоступне (404, paywall) — зафіксуй у нотатці:
   status: unavailable
   Напиши що відомо з назви/abstract

=== ПРІОРИТЕТ ===

Спочатку обробляй ГРУПИ 1, 2, 5 (найбільш релевантні до Stage 1).
Потім ГРУПИ 3, 4, 6 (GPU та drone detection).
Останніми ГРУПИ 7, 8.

=== ФІНАЛ ===

Після всіх посилань:
- Оновити /obsidian-vault/research/sources.md — додати секцію "KB-extra: 40 зовнішніх посилань"
- Звітувати: "KB-extra done: [N] посилань оброблено, [M] недоступних"
