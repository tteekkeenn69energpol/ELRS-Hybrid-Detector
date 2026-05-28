cmake_minimum_required(VERSION 3.16)
project(cfar2d CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Per CLAUDE.md: -O3 -mavx2 -march=native, plus strict warnings.
add_compile_options(
    -O3
    -mavx2
    -march=native
    -Wall
    -Wextra
    -Wpedantic
    -ffast-math
)

find_package(Threads REQUIRED)

# Library: 2D OS-CFAR core.
add_library(cfar2d STATIC cfar2d.cpp)
target_include_directories(cfar2d PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Inline micro-benchmark / self-test executable.
add_executable(bench_cfar2d bench_main.cpp)
target_link_libraries(bench_cfar2d PRIVATE cfar2d Threads::Threads)
