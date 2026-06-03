---
tags: [stage-2, knowledge-builder, oot, gnuradio, setup, cmake]
created: 2026-05-29
type: howto
stage: 2
status: done
source: OOT_Module_Setup_Instructions.md
drive_id: 1NfzqkcGYhJG0t9qfcF7CLCCs0sn4b-II
---

# Повна інструкція: Створення GNU Radio OOT-модуля `gr-elrs_detector`

---

## Крок 0: Підготовка середовища

```bash
sudo apt update
sudo apt install gnuradio gnuradio-dev gr-osmosdr python3-pybind11 \
    python3-numpy python3-scipy python3-matplotlib cmake git

python3 -m venv ~/gr_dev_env
source ~/gr_dev_env/bin/activate

gnuradio-config-info --version
python3 -c "import gnuradio; print(gnuradio.__version__)"
```

---

## Крок 1: Створення OOT-модуля

```bash
mkdir -p ~/gnuradio-projects
cd ~/gnuradio-projects

gr_modtool newmod elrs_detector
cd gr-elrs_detector
```

---

## Крок 2: Додавання блоків

```bash
# Stage 1 — 2D OS-CFAR (C++)
gr_modtool add -t general -l cpp os_cfar_2d

# Stage 2 — Blind Parameter Estimator (Python)
gr_modtool add -t general -l python blind_estimator

# Stage 3 — Dechirping Matched Filter (C++)
gr_modtool add -t general -l cpp dechirp_matched

# Stage 4 — Neural Verifier (Python)
gr_modtool add -t general -l python nelora_verifier

# Stage 5 — Decision Fusion (Python)
gr_modtool add -t general -l python decision_fusion
```

---

## Крок 3: CMakeLists.txt (CUDA + Torch)

```cmake
find_package(CUDA)
find_package(Python3 COMPONENTS Interpreter Development NumPy)
find_package(Torch)

include_directories(${CUDA_INCLUDE_DIRS} ${Python3_INCLUDE_DIRS} ${TORCH_INCLUDE_DIRS})

target_link_libraries(gnuradio-elrs_detector
    ${CUDA_LIBRARIES}
    ${TORCH_LIBRARIES}
    cupy
)
```

---

## Крок 4: Структура після створення

```
gr-elrs_detector/
├── CMakeLists.txt
├── include/elrs_detector/
│   ├── api.h
│   └── os_cfar_2d.h
├── lib/
│   ├── os_cfar_2d_impl.cc
│   └── dechirp_matched_impl.cc
├── python/elrs_detector/
│   ├── __init__.py
│   ├── blind_estimator.py
│   ├── nelora_verifier.py
│   └── decision_fusion.py
├── examples/elrs_full_detector.grc
└── docs/
```

---

## Крок 5: C++ блок os_cfar_2d (скелет)

```cpp
class os_cfar_2d_impl : public os_cfar_2d {
public:
    os_cfar_2d_impl(int guard_x, int guard_y, int train_x, int train_y, float threshold_db);
    int general_work(int noutput_items,
                     gr_vector_int &ninput_items,
                     gr_vector_const_void_star &input_items,
                     gr_vector_void_star &output_items) override;
private:
    cudaStream_t d_stream;
};
```

---

## Крок 6: Компіляція та встановлення

```bash
cd ~/gnuradio-projects/gr-elrs_detector
mkdir build && cd build

cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
make -j$(nproc)
sudo make install
sudo ldconfig

# Перевірка: новий блок "ELRS Detector" у GRC
gnuradio-companion
```

---

## Найкращі практики

- Message Passing між етапами замість потокових даних де можливо.
- Stage 1 на C++/CUDA. Stage 2, 4 — Python + CuPy/Torch.
- Tagged Streams або PDU для передачі метаданих (SF, BW, confidence).
- Runtime Parameter для всіх ключових налаштувань.
- Профілювання — час виконання кожного Stage.

---

## Посилання

- [[stage2-tz-gnuradio]] — ТЗ на інтеграцію
- [[07-oot-gnuradio-skeleton]] — базовий OOT скелет (KB-2)
- [[stage2-flowgraph]] — приклад flowgraph
- [[ext-github-gnuradio-32]] — gr-cuda
