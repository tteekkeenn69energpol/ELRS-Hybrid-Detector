# GitHub репозиторії — зовнішні референси

---
tags: [github, gnuradio, lora, elrs, external, reference]
created: 2026-05-28
type: reference
stage: all
status: ready
---

## 1. gr-lora (lora-net)

**URL**: https://github.com/lora-net  
**Що це**: GNU Radio реалізація LoRa фізичного рівня  
**Релевантність**: Stage 3 (Dechirping + Matched Filter) базується на цьому коді

### Ключові блоки для вивчення
- Whitening / Dewhitening
- CFO / STO корекція
- LoRa RX / TX блоки
- Деmodulation pipeline

### Використання в проєкті
- [[../research/07-oot-gnuradio-skeleton]] — наш OOT модуль базується на gr-lora
- [[../research/10-gnuradio-flowgraph]] — flowgraph використовує gr-lora-sdr
- [[../research/20-grcon25-elrs-gnuradio-paper]] — FAU реалізація ELRS будувалась на gr-lora

---

## 2. ExpressLRS (oficійний firmware)

**URL**: https://github.com/expresslrs/expresslrs  
**Що це**: Офіційний відкритий firmware ELRS  
**Релевантність**: FHSS алгоритм, LCG константи, пакетна структура

### Критично важливі файли для вивчення
```
src/lib/
  FHSS/        ← алгоритм frequency hopping
  CRC/         ← CRC16 реалізація
  SX1280/      ← драйвер чіпа 2.4 GHz
  SX127x/      ← драйвер чіпа 900 MHz
```

### Ключові константи (вже відомі з GRCon25)
```cpp
// LCG для FHSS sequence generation
#define LCG_MULT  0x000343FD
#define LCG_ADD   0x00269EC3

// UID = MD5(binding_phrase)[:6]
// Fisher-Yates shuffle з LCG seed → hopping sequence
```

### Використання в проєкті
- [[../research/16-edge-ai-fhss-tracker]] — FHSS Tracker реверсує цей алгоритм
- [[../research/20-grcon25-elrs-gnuradio-paper]] — FAU реалізація FHSS Controller

---

## Задачі для агентів

| Агент | Задача |
|-------|--------|
| DSP Research | Вивчити FHSS алгоритм з expresslrs/expresslrs → уточнити параметри |
| C++ Dev | Взяти gr-lora як референс для Stage 3 інтерфейсу |
| Docs | Додати ці репо в sources.md |
