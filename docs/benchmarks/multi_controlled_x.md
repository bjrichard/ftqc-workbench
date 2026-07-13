# Multi-controlled Pauli-X benchmark

## Purpose

This benchmark records logical resource estimates for the implemented
clean-ancilla multi-controlled Pauli-X construction.

It benchmarks the fixed control counts defined in the project roadmap:

- 2
- 3
- 4
- 5
- 8
- 16

The benchmark measures logical circuit structure. It does not measure
wall-clock runtime, physical qubits, routing overhead, error-correction cost,
or hardware execution time.

## Reproduction

Run from the repository root:

```bash
python benchmarks/benchmark_multi_controlled_x.py
```

To regenerate the saved comma-separated values (CSV) results:

```bash
python benchmarks/benchmark_multi_controlled_x.py \
    > docs/benchmarks/multi_controlled_x.csv
```

## Register layout

For a circuit with \(k\) controls:

- controls occupy qubits \(0\) through \(k-1\)
- the target occupies qubit \(k\)
- clean ancillas occupy consecutive qubits beginning at \(k+1\)

For \(k \geq 2\), the construction uses:

\[
N_{\mathrm{ancilla}} = k - 2
\]

and the total logical register width is:

\[
N_{\mathrm{qubits}} = 2k - 1.
\]

The clean-ancilla requirement is recorded separately from
`ResourceEstimate.ancilla_count`. The current circuit Intermediate
Representation (IR) does not retain qubit-role metadata, so the generic
resource estimator reports an ancilla count of zero.

## Results

| Controls | Clean ancillas | Logical qubits | Gates | T gates | Expanded T gates | CNOT gates | Toffoli gates | Serial depth | Parallel depth |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 0 | 3 | 1 | 0 | 7 | 0 | 1 | 1 | 1 |
| 3 | 1 | 5 | 3 | 0 | 21 | 0 | 3 | 3 | 3 |
| 4 | 2 | 7 | 5 | 0 | 35 | 0 | 5 | 5 | 5 |
| 5 | 3 | 9 | 7 | 0 | 49 | 0 | 7 | 7 | 7 |
| 8 | 6 | 15 | 13 | 0 | 91 | 0 | 13 | 13 | 13 |
| 16 | 14 | 31 | 29 | 0 | 203 | 0 | 29 | 29 | 29 |

## Scaling

For \(k \geq 2\), the benchmark confirms:

\[
N_{\mathrm{Toffoli}} = 2k - 3,
\]

\[
N_{\mathrm{gates}} = 2k - 3,
\]

\[
N_{\mathrm{ancilla}} = k - 2,
\]

and

\[
N_{\mathrm{qubits}} = 2k - 1.
\]

Serial and dependency-preserving parallel depth are both:

\[
D = 2k - 3.
\]

The current construction exposes no parallelism under the implemented depth
model because successive Toffoli operations are connected through shared
controls or ancillas.

Under the default analytical Toffoli expansion convention,

\[
1\ \mathrm{Toffoli} = 7\ T,
\]

the expanded T-count is:

\[
N_T^{\mathrm{expanded}} = 7(2k - 3).
\]

## Interpretation

The benchmark reports both primitive and expanded T-counts.

The `T gates` column is the primitive explicit T-gate count: it counts only T
gates that appear directly in the circuit Intermediate Representation (IR).

The `Expanded T gates` column analytically charges each primitive Toffoli gate
the default Toffoli expansion cost:

\[
1\ \mathrm{Toffoli} = 7\ T.
\]

This does not mutate or decompose the circuit. It is a first-order analytical
cost convention, not a full Clifford+T circuit, T-depth estimate, or physical
fault-tolerant resource estimate.

## Limitations

The benchmark does not include:

- dirty-ancilla constructions
- relative-phase Toffoli variants
- actual Toffoli decomposition into Clifford+T
- T-depth
- topology or routing
- gate durations
- measurement or feedforward
- physical error-correction resources
- alternative space-depth tradeoffs
