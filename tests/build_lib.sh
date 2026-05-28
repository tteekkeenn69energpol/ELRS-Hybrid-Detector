#!/usr/bin/env bash
# Build the C ABI wrapper as a shared library for ctypes consumption.
# Mirrors the project CMakeLists.txt flags exactly (Release + AVX2 + native + fast-math).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${HERE}/../src"

g++ -O3 -mavx2 -march=native -ffast-math \
    -Wall -Wextra -Wpedantic \
    -std=c++17 -fPIC -shared \
    -I"${SRC}" \
    "${SRC}/cfar2d.cpp" "${HERE}/cfar2d_c.cpp" \
    -lpthread \
    -o "${HERE}/libcfar2d_c.so"

echo "Built ${HERE}/libcfar2d_c.so"
