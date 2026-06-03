---
tags: [stage-2, knowledge-builder, dechirp, queries, research, stage-3]
created: 2026-05-29
type: queries
stage: 3
status: done
drive_folder_id: 1YKR02MsWSyqnjr2D3bTtOO6IYHScgAsj
drive_doc_id: 16y0b2Cn6jrm4CPOaMeFao-GQ9DwdORwYzvDcIZDcqIs
source: '"LoRa CSS dechirping mathematical derivation orthogonality".docx (Google Drive)'
---

# LoRa CSS Dechirping — Дослідницькі Запити

Пошукові запити для Stage 3 (Dechirp + Matched Filter) та реверс-інжинірингу ELRS.

---

## Група 1: Математика та ортогональність LoRa

Фокус: теорія dechirping, ортогональність символів, matched filter SNR.

- "LoRa CSS dechirping mathematical derivation orthogonality"
- "Matched filter SNR gain properties for Chirp Spread Spectrum"
- "Robustness of LoRa dechirp against phase jitter and AM noise"
- "Interference rejection mechanisms in LoRa CSS matched filters"
- "Impact of Carrier Frequency Offset (CFO) on LoRa FFT peak degradation"
- "Symbol Timing Offset (STO) recovery algorithms for LoRa"
- "Circular cross-correlation implementation for periodic chirps"
- "Fractional frequency offset correction in LoRa demodulation"
- "SX1280 LoRa preamble structure detection theory 2.4GHz"
- "SX1280 datasheet analysis LoRa mode registers preamble detection"

---

## Група 2: GPU pipeline та cuFFT оптимізація

Фокус: real-time реалізація, швидка circular correlation через cuFFT, ring buffers.

- "Efficient circular correlation C++ CUDA implementation"
- "GPU acceleration LoRa correlation cuFFT stream processing"
- "Optimizing memory access patterns for cross-correlation CUDA"
- "LoRa dechirp FFT size optimization 1024 2048 4096"
- "Fixed-point arithmetic LoRa dechirp FPGA implementation"
- "C++ ring buffer management for continuous I/Q streaming"
- "Handling variable SF in real-time dechirping pipeline"
- "Peak detection in noisy spectrum using parabolic interpolation"
- "SX1280 dechirp mode register configuration example"
- "SX1280 vs SX1276 LoRa dechirping differences 2.4GHz vs sub-GHz"

---

## Блок: Реверс-інжиніринг ELRS та SDR інтеграція

Фокус: OTA packet structure, FHSS reconstruction, SDR integration.

1. "ExpressLRS OTA packet structure payload format reverse engineering"
2. "Demodulating LoRa-based ELRS telemetry using SDR and C++"
3. "Extracting CRC and whitening sequence for ExpressLRS 2.4GHz packets"
4. "Real-time FHSS sequence reconstruction and hop interval estimation for ELRS"
5. "Distinguishing ExpressLRS from commercial LoRa and VTx interference"
6. "SDR I/Q stream synchronization for ultra-short packet high-rate FHSS"
7. "SoapySDR or RTL-SDR / HackRF API integration for real-time dechirping"
8. "Blind identification of ExpressLRS binding phrase hash from OTA packets"
9. "Packet Error Rate (PER) analysis for passive ELRS sniffing in high-noise environments"
10. "End-to-end pipeline: SDR I/Q ingestion to GPU OS-CFAR and ELRS decoder"

---

## Пріоритизація для DSP Research (R2-5) та Python Dev (C2-3)

### Найкритичніші запити:
- **"cuFFT circular correlation CUDA"** → C2-3 (CWT BW Estimator) + Stage 3 impl
- **"CFO STO recovery algorithms LoRa"** → R2-2 + Stage 3 CFO/STO correction
- **"Peak detection parabolic interpolation"** → sub-bin accuracy для ToA
- **"Double buffering CPU GPU LoRa dechirp"** → performance optimization

---

## Посилання

- [[stage2-dechirp-math]] — математика dechirping та ортогональність
- [[stage2-tz-dechirp-mf]] — ТЗ Stage 3
- [[02-tz1-dechirp-mf]] — аналіз TZ#1 (KB-2)
- [[ext-lora-detection-09]] — LoRa preamble detection
- [[ext-lora-detection-10]] — ELRS FAQ
