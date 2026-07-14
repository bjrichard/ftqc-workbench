# Technical Details

This document contains the lower-level formulas, conventions, limitations, and future directions that support the main project README.

## Supported primitive gates

| Gate | Arity | Resource-model class |
|---|---:|---|
| `I` | 1 | Clifford |
| `X` | 1 | Clifford |
| `Y` | 1 | Clifford |
| `Z` | 1 | Clifford |
| `H` | 1 | Clifford |
| `S` | 1 | Clifford |
| `T` | 1 | non-Clifford |
| `CNOT` | 2 | Clifford |
| `CZ` | 2 | Clifford |
| `TOFFOLI` | 3 | non-Clifford / primitive placeholder |

The project treats `TOFFOLI` as a primitive logical operation in the circuit intermediate representation while also supporting analytical Toffoli-expanded T-count estimates.

## Multi-controlled Pauli-X

For `k >= 2` controls, the clean-ancilla ladder uses:

\[
N_{\mathrm{Toffoli}} = 2k - 3
\]

and requires:

\[
N_{\mathrm{clean\ ancilla}} = k - 2.
\]

The generic resource estimator currently reports `ancilla_count = 0` because the circuit intermediate representation does not retain qubit-role metadata. Construction-level ancilla requirements are documented separately in benchmark outputs.

## Cuccaro-style modular adder

The target operation is:

\[
|a\rangle |b\rangle |0\rangle
\mapsto
|a\rangle |a+b \bmod 2^n\rangle |0\rangle.
\]

Conventions:

- `a[0]` and `b[0]` are least-significant bits.
- `a` and `b` are equal-width, nonempty, disjoint registers.
- `a` is preserved.
- `b` is overwritten with the modular sum.
- One clean work qubit is required.
- The clean work qubit starts in `|0>` and is restored to `|0>`.

Implemented cases:

- compact one-bit modular adder
- compact two-bit modular adder
- general Cuccaro-style majority/unmajority-and-add construction for `n >= 3`

For `n >= 3`, the benchmarked construction has:

\[
N_{\mathrm{Toffoli}} = 2n,
\]

\[
N_{\mathrm{CNOT}} = 4n,
\]

\[
N_{\mathrm{gates}} = 6n.
\]

## Primitive resource estimates

Primitive estimates count exactly what the circuit builder emits.

For example, a circuit containing five primitive Toffoli gates and no explicit T gates has:

```text
toffoli_count = 5
t_count = 0
```

This does not imply zero fault-tolerant T-cost. It means no primitive `T` operations appear directly in the current circuit intermediate representation.

## Toffoli-expanded estimates

The current default convention is:

\[
1\ \mathrm{Toffoli} = 7\ T.
\]

Therefore:

\[
N_T^{\mathrm{expanded}}
=
N_T^{\mathrm{primitive}}
+
7N_{\mathrm{Toffoli}}.
\]

This is a first-order analytical accounting convention. It is not:

- an explicit Clifford+T circuit decomposition
- a T-depth estimate
- a physical fault-tolerant resource estimate
- a hardware runtime estimate

## Verification strategy

Verification includes:

- exhaustive clean-ancilla truth-table checks for multi-controlled Pauli-X
- deterministic randomized checks for larger multi-controlled Pauli-X circuits
- exhaustive truth-table checks for two- and three-bit adders
- deterministic randomized clean-work checks for larger Cuccaro adders
- circuit-equivalence checks up to global phase where applicable
- benchmark regression tests

## Benchmark outputs

The formulas in this document are reflected in the generated benchmark outputs:

- [`benchmarks/multi_controlled_x.md`](benchmarks/multi_controlled_x.md)
- [`benchmarks/multi_controlled_x.csv`](benchmarks/multi_controlled_x.csv)
- [`benchmarks/cuccaro_adder.md`](benchmarks/cuccaro_adder.md)
- [`benchmarks/cuccaro_adder.csv`](benchmarks/cuccaro_adder.csv)

The Markdown benchmark notes explain the generated tables, and the comma-separated values (CSV) files are produced by the benchmark scripts in `benchmarks/`.

## Detailed limitations

The project currently does not estimate or model:

- physical qubit count
- surface-code distance
- code cycles
- magic-state factory footprint or throughput
- distillation cost
- measurement cost
- feedforward latency
- routing overhead
- swap overhead
- hardware topology constraints
- calibration-dependent performance
- crosstalk
- gate-level noise
- noise-aware resource cost
- wall-clock runtime
- scheduled hardware depth
- T-depth
- explicit Toffoli circuit decomposition
- arbitrary gate-synthesis cost
- global circuit rescheduling
- optimal circuit depth under algebraic rewrites

These omissions are deliberate. The current workbench operates at the logical circuit and first-order resource-accounting level.

## Future directions

Potential extensions include:

- explicit ancilla-role metadata in the circuit intermediate representation
- actual Toffoli decomposition into Clifford+T gates
- T-depth estimation under a named decomposition convention
- decomposition-aware CNOT and Clifford counts
- simple readout-error mitigation
- simple stochastic noise models
- routing-aware estimates for constrained connectivity
- pass-based compilation infrastructure
- before-and-after resource estimates for compiler passes
- additional reversible arithmetic primitives, including subtraction, controlled addition, modular reduction, and multiplication

Future work should remain narrowly scoped and testable rather than attempting to turn the repository into a production compiler or full physical resource estimator.
