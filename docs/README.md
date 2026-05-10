# PTX-ASM Quadratic Solver

A high-performance, double-precision quadratic equation solver that bridges the gap between bare-metal x86_64 Assembly and NVIDIA GPU PTX. This project implements a direct analytic solver for complex-coefficient quadratic equations, optimized for massive parallel throughput.

---

## Overview

Unlike standard implementations, this project avoids high-level language overhead by using a host driver written entirely in x86_64 Assembly. It manages the CUDA Driver API context, handles Linux system calls for file I/O, and orchestrates GPU kernel execution with strict ABI compliance.

### Key Features

- **Analytic GPU Kernel**  
  A PTX-based solver using the quadratic formula, optimized with `fma.rn.f64` for maximum precision.

- **Bare-Metal Host**  
  x86_64 Assembly driver that parses CSV data using `mmap` and `sscanf`.

- **ABI Compliant**  
  Strict 16-byte stack alignment ensuring stability when calling C library functions (`printf`, `malloc`, `sscanf`).

- **Multi-Arch Ready**  
  Structured for cross-architecture support (`x86_64` / `AArch64`).

- **High Precision**  
  Full `f64` (Double Precision) support for both real and imaginary components.

---

## Project Structure

```text
.
├── meson.build               # Root build configuration
├── scripts/                  # Python utility suite
│   ├── generate_equations.py # Data generation for testing
│   ├── verify_results.py     # High-precision CPU-based verification
│   └── fuzzy_diff.py         # Floating-point comparison tool
├── src/
│   ├── meson.build           # Source logic and arch-detection
│   └── x86_64/
│       ├── quadratic_solver.s # x86_64 Host Driver (Assembly)
│       └── kernel.ptx         # GPU Solver Kernel (PTX)
└── test/
    └── test.sh               # Full end-to-end CI/CD pipeline script
```

---

## Requirements

- **NVIDIA GPU**  
  Pascal architecture or newer (Compute Capability 6.1+)

- **CUDA Toolkit**  
  Required for `nvcc` and CUDA Driver API headers

- **Build System**  
  `meson` and `ninja`

- **Assembler**  
  `gcc` (GNU AS)

- **Python 3**  
  Used for testing and verification scripts

---

## Build & Debug

### Production Build

Compile for maximum performance:

```bash
meson setup build --buildtype=release
ninja -C build
```

### Debug Build

Includes DWARF symbols for GDB and CUDA `-G` device debugging:

```bash
meson setup build --buildtype=debug
ninja -C build
```

---

## Testing

The included `test.sh` script automates the complete validation pipeline:

1. Cleans previous builds
2. Compiles the Assembly host and PTX kernel
3. Generates 50,000 random complex quadratic equations
4. Executes the GPU solver
5. Verifies the results against a high-precision Python reference

Run the full pipeline:

```bash
./test/test.sh
```

---

## Technical Details

### Memory Alignment

To ensure coalesced memory access on the GPU, the host aligns each equation row to 64 bytes. This guarantees that each thread accesses 64-bit doubles on aligned boundaries, maximizing memory throughput and bus efficiency.

### Complex Math

The solver handles the complex discriminant:

```math
\Delta = b^2 - 4ac
```

and utilizes a sign-aware complex square root implementation to ensure roots are correctly placed in the complex plane.

Quadratic solution formula:

```math
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
```

### Precision Strategy

The PTX kernel uses IEEE-754 compliant double-precision instructions and leverages:

```ptx
fma.rn.f64
```

to reduce rounding error during discriminant evaluation and root computation.

---

## Architecture Notes

### Host Responsibilities

The x86_64 Assembly host performs:

- CUDA Driver API initialization
- PTX module loading
- Kernel launch configuration
- CSV parsing
- GPU memory management
- Result serialization

### GPU Responsibilities

Each CUDA thread independently solves one quadratic equation with complex coefficients using a direct analytic method.

This design scales efficiently across large datasets with minimal CPU intervention.

---

## Performance Goals

The project is designed around:

- Minimal runtime overhead
- Zero high-level runtime dependencies
- Massive parallel equation solving
- High numerical stability
- Efficient GPU memory access patterns

---

## Future Work

Planned extensions include:

- Native AArch64 Assembly host
- CRC32-based validation paths
- Binary input format support
- Multi-GPU scheduling
- SIMD-optimized CPU fallback solver
- Move away from libc and libcuda using IOCTL syscalls

---

## License

This project is released under the MIT License.

You are free to use, modify, distribute, and integrate this software into personal, academic, or commercial projects.

> Available for "the entire world".

---