---
tags: [external, KB-extra, group-4, cuda, numba, python, kernels, docs]
created: 2026-05-28
type: docs
stage: 1
source_url: https://numba.pydata.org/numba-doc/dev/cuda/kernels.html
status: done
---

# Numba CUDA kernels (Python @cuda.jit)

## Опис
Numba дозволяє **писати CUDA kernels у Python** через `@cuda.jit` декоратор. Grid-block-thread ієрархія як у C++.

## Key syntax
```python
from numba import cuda

@cuda.jit
def my_kernel(arr):
    idx = cuda.grid(1)
    if idx < arr.size:
        arr[idx] *= 2

# Launch:
my_kernel[blocks_per_grid, threads_per_block](array)
```

Thread positioning:
- `cuda.threadIdx`, `cuda.blockIdx`, `cuda.blockDim`, `cuda.gridDim`
- Shortcut: `cuda.grid(ndim)` для absolute position

## Limitations
- Kernels can't return values → write to passed arrays
- No dynamic parallelism (no device-side kernel launch)
- Boundary check обов'язковий якщо grid×block ≠ array size
- Implicit host-device transfers — **synchronous**

## vs CuPy
- **Numba**: finer-grained thread control, custom kernels
- **CuPy**: NumPy-compatible, швидке prototyping
- **Гібрид**: CuPy для bulk ops + Numba для custom kernel (наш Stage 2 [[09-stage2-blind-estimator-py]])

## Релевантність
- **Stage 2 (Python/CuPy)**: коли потрібен custom kernel поза CuPy operations (e.g., специфічний DWT scaling, custom CFO correction) — Numba дешевший за писання C++/CUDA
- Хороша середина між Python (легко) і C++/CUDA (швидко)
- Для production Stage 1 все одно треба C++ ([[07-oot-gnuradio-skeleton]])

## Посилання
- [[09-stage2-blind-estimator-py]] — наш Python Stage 2
- [[ext-cuda-gpu-22]] — shared memory концепти
- [[19-full-cuda-cpp-pipeline]] — для C++ production порівняння
