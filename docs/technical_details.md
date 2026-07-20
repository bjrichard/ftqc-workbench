# Technical details

This document contains the lower-level formulas, conventions, limitations, and
future directions that support the main project README.

## Supported primitive gates

| Gate | Arity | Expected class |
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

The project treats `TOFFOLI` as a primitive logical operation in the circuit
intermediate representation while also supporting analytical
Toffoli-expanded T-count estimates.

## Circuit and bit-ordering conventions

Qubits are represented by zero-based integer indices.

For circuit operations, qubit order follows the relevant gate convention:

- Controlled-NOT (CNOT): `(control, target)`
- Controlled-Z (CZ): `(qubit_0, qubit_1)`
- Toffoli: `(control_0, control_1, target)`

For integer registers, register index `0` is the least-significant bit:

```text
a[0] = least-significant bit of register a
b[0] = least-significant bit of register b
```

For displayed measurement bitstrings, the convention is:

```text
"q_{n-1}...q_1q_0"
```

The rightmost character is qubit 0 and the least-significant bit. Therefore,
binary-ordered bitstrings appear as:

```text
"00", "01", "10", "11", ...
```

for two or more qubits.

## Multi-controlled Pauli-X

For `k >= 2` controls, the clean-ancilla ladder uses:

\[
N_{\mathrm{Toffoli}} = 2k - 3
\]

and requires:

\[
N_{\mathrm{clean\ ancilla}} = k - 2.
\]

The generic resource estimator currently reports `ancilla_count = 0` because
the circuit intermediate representation does not retain qubit-role metadata.
Construction-level ancilla requirements are documented separately in benchmark
outputs.

Implemented cases:

- one control: `CNOT`
- two controls: `TOFFOLI`
- three or more controls: clean-ancilla Toffoli ladder

Benchmark artifacts:

```text
benchmarks/benchmark_multi_controlled_x.py
docs/benchmarks/multi_controlled_x.csv
docs/benchmarks/multi_controlled_x.md
```

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

Benchmark artifacts:

```text
benchmarks/benchmark_cuccaro_adder.py
docs/benchmarks/cuccaro_adder.csv
docs/benchmarks/cuccaro_adder.md
```

## Primitive resource estimates

Primitive estimates count exactly what the circuit builder emits.

For example, a circuit containing five primitive Toffoli gates and no explicit
T gates has:

```text
toffoli_count = 5
t_count = 0
```

This does not imply zero fault-tolerant T-cost. It means no primitive `T`
operations appear directly in the current circuit intermediate representation.

The primitive resource estimator currently reports:

- total gate count
- explicit primitive T-gate count
- Controlled-NOT (CNOT) count
- Controlled-Z (CZ) count
- Toffoli count
- logical qubit count
- ancilla count
- serial depth
- dependency-preserving parallel depth

The `ancilla_count` field currently remains zero because the generic circuit
object does not retain role metadata after construction.

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
- a magic-state factory estimate

## Readout-error mitigation

The workbench includes classical readout-error mitigation in
`qc_compiler.mitigation`.

This feature acts on measured classical counts after circuit execution or
simulation. It does not modify circuits and does not simulate noisy quantum
evolution.

Implemented public helpers:

```python
from qc_compiler.mitigation import (
    mitigate_single_qubit_readout,
    mitigate_tensor_product_readout,
)
```

### Single-qubit readout mitigation

The single-qubit model uses a 2-by-2 assignment matrix:

\[
A =
\begin{pmatrix}
P(0_{\mathrm{meas}}|0_{\mathrm{true}}) &
P(0_{\mathrm{meas}}|1_{\mathrm{true}}) \\
P(1_{\mathrm{meas}}|0_{\mathrm{true}}) &
P(1_{\mathrm{meas}}|1_{\mathrm{true}})
\end{pmatrix}.
\]

The assignment-matrix convention is:

```text
assignment_matrix[measured_bit, true_bit]
```

The linear model is:

\[
p_{\mathrm{meas}} = A p_{\mathrm{true}}.
\]

Mitigation solves:

\[
p_{\mathrm{true}} \approx A^{-1}p_{\mathrm{meas}}.
\]

The implementation uses `np.linalg.solve` rather than explicitly forming the
inverse.

### Tensor-product multi-qubit readout mitigation

The tensor-product helper supports independent per-qubit readout errors.

For assignment matrices:

```text
(A_0, A_1, ..., A_{n-1})
```

where `A_q` is the assignment matrix for qubit `q`, the full assignment matrix
is built as:

\[
A_{\mathrm{full}} = A_{n-1} \otimes \cdots \otimes A_1 \otimes A_0.
\]

This order matches the displayed bitstring convention:

```text
"q_{n-1}...q_1q_0"
```

where the rightmost bit is qubit 0.

The tensor-product mitigation helper returns probabilities for every
computational-basis bitstring in binary order.

### Numerical convention

Linear inversion can produce negative entries because of finite-shot noise or
ill-conditioned assignment matrices.

The implemented convention is:

1. solve the linear system
2. clip negative entries to zero
3. renormalize the probability vector

This is simple and inspectable, but it is not a statistically optimal
constrained estimator.

### Readout-mitigation limitations

The mitigation module does not currently support:

- correlated readout-error models
- full `2**n` by `2**n` correlated assignment matrices as public input
- calibration fitting
- uncertainty estimates
- covariance propagation
- Bayesian mitigation
- constrained least-squares mitigation
- quasiprobability mitigation
- gate-noise simulation
- density-matrix simulation
- hardware backend integration

Related documentation:

```text
docs/readout_mitigation_notes.md
docs/readout_mitigation_example.md
```

## Verification strategy

Verification includes:

- exhaustive clean-ancilla truth-table checks for multi-controlled Pauli-X
- deterministic randomized checks for larger multi-controlled Pauli-X circuits
- exhaustive truth-table checks for two- and three-bit adders
- deterministic randomized clean-work checks for larger Cuccaro adders
- circuit-equivalence checks up to global phase where applicable
- benchmark regression tests
- deterministic tests for single-qubit readout mitigation
- deterministic tests for tensor-product multi-qubit readout mitigation

## Detailed limitations

The project currently does not estimate or model:

- physical qubit count
- surface-code distance
- code cycles
- magic-state factory footprint or throughput
- distillation cost
- measurement cost inside the circuit intermediate representation
- feedforward latency
- routing overhead
- swap overhead
- hardware topology constraints
- calibration-dependent performance
- crosstalk
- gate-level noise
- noisy quantum evolution
- noise-aware resource cost
- wall-clock runtime
- scheduled hardware depth
- T-depth
- explicit Toffoli circuit decomposition
- arbitrary gate-synthesis cost
- global circuit rescheduling
- optimal circuit depth under algebraic rewrites

These omissions are deliberate. The current workbench operates at the logical
circuit, exact verification, first-order resource-accounting, and classical
readout-post-processing level.

## Future directions

Potential extensions include:

- explicit ancilla-role metadata in the circuit intermediate representation
- actual Toffoli decomposition into Clifford+T gates
- T-depth estimation under a named decomposition convention
- decomposition-aware CNOT and Clifford counts
- correlated readout-error mitigation
- constrained least-squares readout mitigation
- simple stochastic noise models
- routing-aware estimates for constrained connectivity
- pass-based compilation infrastructure
- before-and-after resource estimates for compiler passes
- additional reversible arithmetic primitives, including subtraction,
  controlled addition, modular reduction, and multiplication

Future work should remain narrowly scoped and testable rather than attempting
to turn the repository into a production compiler or full physical resource
estimator.
