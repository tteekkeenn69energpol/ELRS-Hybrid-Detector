# Повна інструкція: Створення GNU Radio OOT-модуля `gr-elrs_detector`

---

## Крок 0: Підготовка середовища

```bash
# 1. Встановлення необхідного ПЗ
sudo apt update
sudo apt install gnuradio gnuradio-dev gr-osmosdr python3-pybind11 python3-numpy python3-scipy python3-matplotlib cmake git

# 2. Активуємо Python venv (рекомендовано)
python3 -m venv ~/gr_dev_env
source ~/gr_dev_env/bin/activate

# 3. Перевіряємо версії
gnuradio-config-info --version
python3 -c "import gnuradio; print(gnuradio.__version__)"
```

---

## Крок 1: Створення OOT-модуля за допомогою gr_modtool

```bash
# Переходимо в робочу директорію
mkdir -p ~/gnuradio-projects
cd ~/gnuradio-projects

# Створюємо модуль
gr_modtool newmod elrs_detector

cd gr-elrs_detector
```

---

## Крок 2: Додавання основних блоків

```bash
# Stage 1 — 2D OS-CFAR (C++ для швидкості)
gr_modtool add -t general -l cpp os_cfar_2d

# Stage 2 — Blind Parameter Estimator (Python)
gr_modtool add -t general -l python blind_estimator

# Stage 3 — Dechirping Matched Filter (C++)
gr_modtool add -t general -l cpp dechirp_matched

# Stage 4 — Neural Verifier (Python)
gr_modtool add -t general -l python nelora_verifier

# Додатковий блок для Message Fusion
gr_modtool add -t general -l python decision_fusion
```

---

## Крок 3: Налаштування CMakeLists.txt (критично важливо)

```cmake
# Додати в кінець файлу
find_package(CUDA)
find_package(Python3 COMPONENTS Interpreter Development NumPy)
find_package(Torch)

include_directories(
    ${CUDA_INCLUDE_DIRS}
    ${Python3_INCLUDE_DIRS}
    ${TORCH_INCLUDE_DIRS}
)

# Додати залежності
target_link_libraries(gnuradio-elrs_detector
    ${CUDA_LIBRARIES}
    ${TORCH_LIBRARIES}
    cupy
)
```

---

## Крок 4: Структура модуля після створення

```
gr-elrs_detector/
├── CMakeLists.txt
├── include/elrs_detector/
│   ├── api.h
│   └── os_cfar_2d.h
├── lib/
│   ├── os_cfar_2d_impl.cc
│   ├── dechirp_matched_impl.cc
├── python/elrs_detector/
│   ├── __init__.py
│   ├── blind_estimator.py
│   ├── nelora_verifier.py
│   └── decision_fusion.py
├── python/bindings/
├── examples/elrs_full_detector.grc
├── apps/
└── docs/
```

---

## Крок 5: Приклад реалізації C++ блоку (os_cfar_2d)

У файлі `lib/os_cfar_2d_impl.cc`:

```cpp
class os_cfar_2d_impl : public os_cfar_2d
{
public:
    os_cfar_2d_impl(int guard_x, int guard_y, int train_x, int train_y, float threshold_db);
   
    int general_work(int noutput_items,
                     gr_vector_int &ninput_items,
                     gr_vector_const_void_star &input_items,
                     gr_vector_void_star &output_items) override;
private:
    // CUDA stream, buffers тощо
    cudaStream_t d_stream;
};
```

---

## Крок 6: Компіляція та встановлення модуля

```bash
cd ~/gnuradio-projects/gr-elrs_detector
mkdir build && cd build

cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
make -j$(nproc)
sudo make install
sudo ldconfig
```

**Перевірка встановлення:**

```bash
gnuradio-companion
# Повинен з'явитись новий блок "ELRS Detector" в категорії "elrs_detector"
```

---

## Крок 7: Створення прикладу Flowgraph

Створіть файл `examples/elrs_full_pipeline.grc` з наступними блоками:

1. **Soapy SDR Source** (Aaronia)
2. **OS_CFAR_2D**
3. **Message Debug** (для Stage 1)
4. **Blind Estimator** (Python)
5. **Dechirp Matched**
6. **NELoRa Verifier**
7. **File Sink** + **UDP Sink** для результатів

---

## Крок 8: Рекомендовані найкращі практики

- Використовуйте **Message Passing** між етапами замість потокових даних де можливо.
- Stage 1 робіть на C++/CUDA.
- Stage 2, 4 — Python + CuPy/Torch.
- Використовуйте **Tagged Streams** або **PDU** для передачі метаданих (SF, BW, confidence).
- Додайте **Runtime Parameter** для всіх ключових налаштувань.
- Реалізуйте **профілювання** (час виконання кожного Stage).
