# THEORY.md

## Overview

The program solves quadratic equations of the form:

```math
ax^2 + bx + c = 0
```

where:

```math
a,b,c \in \mathbb{C}
```

The implementation uses a direct analytic solution executed on an NVIDIA GPU through a PTX kernel.

Each GPU thread processes exactly one equation independently.

No iterative numerical method is used.

---

# Execution Model

The host program:

1. Loads equation data into GPU memory.
2. Launches the PTX kernel.
3. Assigns one CUDA thread per equation.
4. Retrieves computed roots.

The kernel operates in SIMD/SIMT fashion across many equations simultaneously.

---

# Input Layout

Each equation occupies 64 bytes.

Structure:

```text
Offset  Size  Description
0       8     a.real
8       8     a.imag
16      8     b.real
24      8     b.imag
32      8     c.real
40      8     c.imag
48      16    padding
```

Padding is used to align rows to cache and memory transaction boundaries.

---

# Thread Indexing

The global thread index is computed as:

```math
idx = blockIdx.x \cdot blockDim.x + threadIdx.x
```

Threads with:

```math
idx \ge N
```

exit immediately.

---

# Coefficient Representation

Complex numbers are represented explicitly as two `f64` values:

```text
(real, imaginary)
```

No packed complex datatype is used.

Example:

```math
a = a_1 + ia_2
```

---

# Discriminant Computation

The kernel computes:

```math
\Delta = b^2 - 4ac
```

using explicit complex arithmetic.

---

## Complex Square

For:

```math
b = b_1 + ib_2
```

the square is:

```math
b^2 =
(b_1^2 - b_2^2)
+
i(2b_1b_2)
```

---

## Complex Multiplication

For:

```math
a = a_1 + ia_2
```

and:

```math
c = c_1 + ic_2
```

the product is:

```math
ac =
(a_1c_1 - a_2c_2)
+
i(a_1c_2 + a_2c_1)
```

---

# Complex Square Root

The discriminant square root is computed analytically.

Given:

```math
d = d_r + id_i
```

first compute magnitude:

```math
|d| = \sqrt{d_r^2 + d_i^2}
```

Then:

```math
u = \sqrt{\frac{|d| + d_r}{2}}
```

```math
v = \sqrt{\frac{|d| - d_r}{2}}
```

Result:

```math
\sqrt{d} = u + iv
```

The sign of `v` is adjusted according to the sign of `d_i`.

This selects the correct complex half-plane.

---

# Root Computation

The quadratic formula is applied directly:

```math
x =
\frac{-b \pm \sqrt{\Delta}}{2a}
```

Two numerators are generated:

```math
-b + \sqrt{\Delta}
```

and:

```math
-b - \sqrt{\Delta}
```

---

# Complex Division

Division is implemented using conjugates.

For:

```math
\frac{p+iq}{r+is}
```

the implementation computes:

```math
\frac{(p+iq)(r-is)}{r^2+s^2}
```

This avoids direct complex division instructions.

---

# Numerical Operations

The kernel primarily uses:

```text
mul.f64
add.f64
sub.f64
sqrt.rn.f64
fma.rn.f64
```

`fma.rn.f64` performs fused multiply-add with IEEE round-to-nearest semantics.

Example:

```math
a \cdot b + c
```

is evaluated with one rounding step.

This reduces accumulated floating-point error.

---

# Memory Access

Input and output rows are aligned to 64 bytes.

This improves:

- global memory coalescing
- cacheline utilization
- warp memory efficiency

Each thread performs:

- 6 input loads
- 4 output stores

All accesses are sequential and fixed-stride.

---

# Output Layout

Each output row contains two complex roots:

```text
Offset  Size  Description
0       8     x1.real
8       8     x1.imag
16      8     x2.real
24      8     x2.imag
```

Remaining bytes are unused.

---

# Precision

All arithmetic uses IEEE-754 double precision (`f64`).

No mixed precision operations are used.

No iterative refinement is performed.

---

# Algorithmic Complexity

Per equation:

```math
O(1)
```

No dependency exists between threads.

Total throughput scales approximately linearly with GPU occupancy.

---

# PTX Characteristics

Target:

```text
sm_61
```

PTX version:

```text
7.0
```

The kernel uses:

- explicit register allocation
- manual complex arithmetic
- branch minimization
- direct global memory addressing

No CUDA runtime abstractions are present.

---

# Failure Conditions

The kernel does not explicitly guard against:

- `a = 0`
- NaN propagation
- INF propagation
- overflow
- underflow

Behavior in these cases follows IEEE-754 semantics.

---

# Design Goals

Primary objectives:

- deterministic execution
- minimal runtime overhead
- high arithmetic throughput
- explicit numerical control
- predictable memory access
- direct GPU execution model

No dynamic allocation occurs inside the kernel.

No recursion or synchronization primitives are used.

---