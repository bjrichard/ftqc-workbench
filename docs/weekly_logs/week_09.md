# Week 9 log — General Cuccaro adder implementation and benchmarks

## Week 9 objective

Complete the integer adder primitive family by moving from small special cases
to a general Cuccaro-style in-place modular adder, then verify and benchmark
the construction.

The target operation is:

\[
|a\rangle |b\rangle |0\rangle
\mapsto
|a\rangle |a+b \bmod 2^n\rangle |0\rangle.
\]

The implementation uses equal-width input registers, preserves the `a`
register, overwrites the `b` register with the modular sum, and restores the
clean work qubit to zero.

## Scope for this week

In scope:

- implement the general Cuccaro majority/unmajority-and-add sequence
- exhaustively verify the first nontrivial general case
- add deterministic randomized verification for larger register widths
- add benchmark infrastructure
- generate a saved comma-separated values (CSV) benchmark table
- document observed logical resource scaling
- add benchmark test coverage

Out of scope:

- carry-in or carry-out variants
- subtraction
- controlled addition
- modular reduction
- multiplication
- Toffoli decomposition into Clifford+T
- T-count from decomposed Toffoli gates
- T-depth
- topology-aware routing
- physical error-correction resource estimates

## Completed work

### Day 1 — General construction

Added an exhaustive `n = 3` truth-table test for `build_cuccaro_adder`.

Implemented the general Cuccaro-style majority/unmajority-and-add sequence for
register widths `n >= 3`.

The implementation keeps the existing compact special cases for:

- `n = 1`
- `n = 2`

The `n = 3` exhaustive test verifies that:

- the `a` register is preserved
- the `b` register becomes `(a + b) mod 2**n`
- the clean work qubit is restored to zero

### Day 2 — Larger-register verification

Added deterministic randomized tests for larger adders:

- `n = 4`
- `n = 8`
- `n = 16`

For each register width, randomized clean-work computational-basis inputs are
sampled and checked against the expected modular addition behavior.

This avoids infeasible exhaustive testing for large registers while keeping the
tests deterministic and reproducible.

### Day 3 — Benchmark infrastructure and documentation

Added:

- `benchmarks/benchmark_cuccaro_adder.py`
- `docs/benchmarks/cuccaro_adder.csv`
- `docs/benchmarks/cuccaro_adder.md`

The benchmark uses the fixed register widths from the project roadmap:

- 2
- 3
- 4
- 8
- 16

Each width is the number of bits in each input register.

The benchmark records:

- register bits
- required clean work qubits
- logical qubits
- gate count
- T gate count
- Controlled-NOT (CNOT) gate count
- Toffoli gate count
- serial depth
- dependency-preserving parallel depth

### Day 4 — Benchmark test coverage

Added tests for the Cuccaro adder benchmark module.

The tests verify:

- benchmark register widths match the roadmap
- benchmark circuits use the expected logical register size
- compact `n = 2` resource counts are stable
- general `n = 4` resource counts are stable
- benchmark result ordering is preserved
- comma-separated values (CSV) output has stable headers and rows
- invalid benchmark inputs are rejected

## Current implementation status

Implemented:

- compact one-bit modular adder
- compact two-bit modular adder
- general Cuccaro-style adder for `n >= 3`
- exhaustive verification for `n = 2` and `n = 3`
- deterministic randomized verification for `n = 4`, `n = 8`, and `n = 16`
- resource benchmark script
- saved benchmark CSV
- benchmark documentation
- benchmark tests

Not implemented:

- arithmetic variants beyond in-place modular addition
- decomposed Toffoli resource estimates
- physical resource estimates

## Register convention

For an `n`-bit adder:

- `a[0]` and `b[0]` are least-significant bits
- tuple entries are circuit qubit indices
- tuple positions are register bit positions
- `a` and `b` are equal-width, nonempty, disjoint registers
- `a` is preserved
- `b` is overwritten with the modular sum
- one clean work qubit is required
- the clean work qubit begins in `|0>` and is restored to `|0>`

The benchmark layout is:

```text
a register:       qubits 0 through n - 1
b register:       qubits n through 2n - 1
clean work qubit: qubit 2n
```

Therefore:

\[
N_{\mathrm{qubits}} = 2n + 1.
\]

## Benchmark summary

Saved benchmark results:

| Register bits | Clean work qubits | Logical qubits | Gates | T gates | CNOT gates | Toffoli gates | Serial depth | Parallel depth |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 5 | 3 | 0 | 2 | 1 | 3 | 2 |
| 3 | 1 | 7 | 18 | 0 | 12 | 6 | 18 | 16 |
| 4 | 1 | 9 | 24 | 0 | 16 | 8 | 24 | 21 |
| 8 | 1 | 17 | 48 | 0 | 32 | 16 | 48 | 41 |
| 16 | 1 | 33 | 96 | 0 | 64 | 32 | 96 | 81 |

For `n >= 3`, the benchmark confirms:

\[
N_{\mathrm{work}} = 1,
\]

\[
N_{\mathrm{qubits}} = 2n + 1,
\]

\[
N_{\mathrm{Toffoli}} = 2n,
\]

\[
N_{\mathrm{CNOT}} = 4n,
\]

\[
N_{\mathrm{gates}} = 6n,
\]

\[
D_{\mathrm{serial}} = 6n,
\]

and the current dependency-preserving parallel-depth estimator reports:

\[
D_{\mathrm{parallel}} = 5n + 1.
\]

The `n = 2` row uses a compact specialized implementation and is excluded
from the general scaling formulas.

## Interpretation

The benchmark treats Toffoli as a primitive logical gate. Consequently:

- T-count is zero
- Toffoli decomposition cost is not included
- T-depth is not estimated
- physical fault-tolerant cost is not represented

These results describe the high-level logical circuit construction currently
implemented in the workbench.

## End-of-week review

1. What was completed?
   - General Cuccaro-style adder implementation, exhaustive `n = 3`
     verification, randomized large-register verification, benchmark
     infrastructure, saved benchmark results, benchmark documentation, and
     benchmark tests.

2. What is behind schedule?
   - Nothing material for the current roadmap. The adder primitive family now
     has implementation, verification, and benchmark coverage.

3. What should be cut?
   - Nothing from the current integer-adder path.

4. What should move to backlog?
   - Carry-in/carry-out variants, subtraction, controlled addition, modular
     reduction, multiplication, arithmetic optimizations, and decomposed
     Clifford+T resource estimation remain deferred.

5. What is next week’s main deliverable?
   - Decide whether to extend arithmetic primitives or shift to resource-model
     improvement, especially Toffoli decomposition and nonzero T-count/T-depth
     accounting.

6. Did any result suggest a publishable angle?
   - No. The result is portfolio-quality primitive implementation and
     benchmarking work, not a novel research contribution.

7. Do any scope-cut triggers apply?
   - No.
