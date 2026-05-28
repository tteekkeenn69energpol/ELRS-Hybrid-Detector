# GRCon25 — Implementation and Analysis of ExpressLRS Under Interference Using GNU Radio

---
tags: [grcon25, gnuradio, elrs, lora, fhss, css, interference, external, paper]
created: 2026-05-28
type: paper
stage: all
status: done
source: GabrielGarcia-FAUCAAI-Grcon25.pdf
url: https://events.gnuradio.org/event/26/contributions/771/attachments/238/622/GabrielGarcia-FAUCAAI-Grcon25.pdf
authors: Gabriel Garcia, Georgios Sklivanitis, Dimitris A. Pados (Florida Atlantic University)
github: https://github.com/Diamond-D0gs/GNU_Radio_ExpressLRS
---

## Короткий зміст

Перша відома відкрита реалізація ExpressLRS у GNU Radio. Побудована на базі `gr-lora-sdr`, додає підтримку FHSS (frequency hopping). Проведено SITL та HITL тести на ADALM-Pluto SDR.

---

## Ключові факти про ELRS протокол

### Фізичний рівень
- Базується на LoRa CSS (Chirp Spread Spectrum) — SX127x / SX1280
- Підтримує 900 MHz та 2.4 GHz ISM діапазони
- SF (Spreading Factor): 7–12, типово SF7 для швидкісних режимів
- BW: 125/250/500 kHz (900 MHz), 203/406/812/1625 kHz (2.4 GHz)
- Пакети малі: 8–13 байт payload

### FHSS алгоритм (критично для детектора)
- UID = MD5(binding_phrase)[:6 bytes]
- LCG seed: константи `0x343FD` і `0x269EC3` (з офіційного firmware)
- Fisher-Yates shuffle на масиві каналів → детермінована псевдовипадкова послідовність
- Hop interval: кожні 1–16 пакетів (4-bit поле у sync пакеті)
- FCC915: **40 каналів**, 23.4 MHz смуга, центр 915 MHz

### Sync пакет (преамбула)
- Містить: поточний FHSS індекс, позиція в round-robin, останні 2 байти UID
- При втраті зв'язку → transmitter входить у search phase (підвищена частота sync)
- **8 up-chirps + 2 SYNC + 2.25 down-chirps** — стандартна преамбула LoRa

---

## Результати тестування (SITL)

### PER vs кількість каналів (SF7, 5000 пакетів)

| Канали | 5 конкурентних Tx | Висновок |
|--------|-------------------|---------|
| 10 ch | висока PER | недостатньо |
| 20 ch | ~2.2 пакети втрачено | погано |
| 30 ch | значно краще | прийнятно |
| **40 ch** | **~1 пакет з 5000** | ✅ відмінно |

→ **Більше каналів = краща стійкість до interference**

### PER vs SF (40 каналів, FCC915)

| SF | Стійкість при 5 Tx |
|----|-------------------|
| SF7 | прогресивне зростання PER |
| SF8–SF10 | 0.4–0.6 пакети з 5000 ✅ |

→ **Вищий SF = більший processing gain = краща стійкість**

### Практичний ліміт SITL
- ~15 конкурентних Tx — більше → timing jitter у GNU Radio scheduler

---

## GNU Radio реалізація

### Ключові блоки

| Блок | Функція |
|------|---------|
| `CounterFormatter` | Генерує 6-байт payload з лічильником |
| `FHSS Controller` | Реалізує ELRS FHSS алгоритм (LCG + Fisher-Yates) |
| `gr-lora-sdr` | LoRa TX/RX фізичний рівень |
| `Signal Source` + `Multiply` | Симулює частотний хоп |

### SITL параметри

```
LoRa sample rate: 250 KSps
BW: 125 kHz
SF: 7 (базово)
Coding rate: 4/5
Resampled BW: 23.4 MHz
Packet rate: 50 Hz (кожні 20 ms)
```

---

## Релевантність до проєкту ELRS Hybrid Detector

### Stage 1 (OS-CFAR) — пряма релевантність
- Підтверджує структуру преамбули: **8 up-chirps** → OS-CFAR має детектувати цей патерн
- FHSS параметри FCC915: 40 каналів, 23.4 MHz → ширина вікна спектрограми
- Sync пакет містить FHSS індекс → після детекції можна передбачити наступний хоп

### Stage 3 (Dechirping + Matched Filter)
- gr-lora-sdr підтверджує CFO/STO корекцію → наш Stage 3 має ті ж алгоритми
- Fisher-Yates LCG реверс → [[../research/16-edge-ai-fhss-tracker]] (FHSS Tracker)

### Stage 4 (FHSS Tracker / Jammer)
- LCG константи відомі (0x343FD, 0x269EC3) + MD5(binding_phrase) = UID
- Теоретично: якщо знаємо UID → можемо відтворити всю hopping sequence
- GitHub: https://github.com/Diamond-D0gs/GNU_Radio_ExpressLRS → код для вивчення

### Обмеження / ризики
- HITL: SDR buffering latency → misalignment FHSS de-hopping (актуально для нашого Stage 1!)
- Timing-critical: FHSS повідомлення мають бути time-aligned із sample stream
- GNU Radio scheduler jitter при >15 Tx → підтверджує вибір C++/CUDA для Stage 1

---

## Корисні посилання

- GitHub реалізація: https://github.com/Diamond-D0gs/GNU_Radio_ExpressLRS
- gr-lora-sdr: посилання з роботи Joachim & Burg 2024
- [[../research/07-oot-gnuradio-skeleton]] — наш OOT модуль
- [[../research/10-gnuradio-flowgraph]] — наш GNU Radio flowgraph
- [[../research/16-edge-ai-fhss-tracker]] — FHSS Tracker (LCG реверс)
- [[../research/08-stage1-oscfar-cpp]] — Stage 1 реалізація
