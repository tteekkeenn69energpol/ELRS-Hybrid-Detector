---
tags: [knowledge-builder, code, stage1, oscfar, cpp, cuda, cmake]
created: 2026-05-28
type: code
stage: 1
status: ready
drive_id: 1tVdVov4TD7-Gc8m1Q_MP9U7BKeexgneWeR146E54bN8
source: 08_stage1_oscfar_cmake_cpp.md
---

# Stage 1: OS-CFAR C++ + CMake (gr-elrs_detector)

## Призначення
Готовий до використання `CMakeLists.txt` та `os_cfar_2d_impl.cc` для C++ блоку GNU Radio.
Фундамент pipeline — має бути максимально оптимізованим.

## CMakeLists.txt — ключові частини
- GNU Radio 3.10+ runtime + blocks
- Python3 + NumPy + pybind11 bindings
- Optional CUDA: `option(ENABLE_CUDA "..." ON)`, окремий `os_cfar_kernels.cu`
- Library: `gnuradio-elrs_detector` з джерелами `os_cfar_2d_impl.cc` + `dechirp_matched_impl.cc`
- Python bindings через `pybind11_add_module`

## OS-CFAR імплементація
- **2D CFAR**: range × doppler / time × frequency cells
- Guard cells + training cells, rank-based threshold (OS = Ordered Statistics)
- CUDA kernel в `lib/cuda/os_cfar_2d_kernel.cu` (опціонально)
- Output: PMT message з координатами піку (time, freq, power)

## Артефакти, які потрібно створити
- `gr-elrs_detector/CMakeLists.txt`
- `lib/os_cfar_2d_impl.cc`, `lib/os_cfar_2d_impl.h`
- `lib/cuda/os_cfar_2d_kernel.cu` (за `ENABLE_CUDA`)
- `python/bindings/os_cfar_2d_python.cc`
- `grc/elrs_detector_os_cfar_2d.block.yml`

## Залежності
- Скелет OOT: [[07-oot-gnuradio-skeleton]]
- Повна CUDA реалізація: [[19-full-cuda-cpp-pipeline]]
- Аналіз STFT+CFAR pipeline: [[17-gpu-stft-cfar-analysis]]
- Дублюється у standalone виді в `NEW_CODE/CFAR_2D_ELRS_915_30MSPS_2048.grc`

## Backlinks (Docs, D-1e)

- Специфікація реалізації (Stage 1): [[../docs/cfar-spec|cfar-spec]] (R-1..R-4, approved)
- Stage 1 QA-вердикт: [[../logs/test-results-2026-05-28|test-results-2026-05-28]] (PASS)
- Лог рішень: [[../logs/decisions-log|decisions-log]] (A-06: rank-only nth_element, A-07: row-stripe tiling)
- Огляд: [[../00-overview/project-overview]], [[../00-overview/architecture]]
