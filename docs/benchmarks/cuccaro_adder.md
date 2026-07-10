# Cuccaro adder benchmark

## Purpose

This benchmark records logical resource estimates for the implemented
Cuccaro-style in-place modular adder.

It benchmarks the fixed register widths defined in the project roadmap:

- 2
- 3
- 4
- 8
- 16

Each width is the number of bits in each input register.

The benchmark measures logical circuit structure. It does not measure
wall-clock runtime, physical qubits, routing overhead, error-correction cost,
or hardware execution time.

## Reproduction

Run from the repository root:

```bash
python benchmarks/benchmark_cuccaro_adder.py
```

To regenerate the saved comma-separated values (CSV) results:

```bash
python benchmarks/benchmark_cuccaro_adder.py \
    > docs/benchmarks/cuccaro_adder.csv
```

## Register layout

For an adder with \(n\)-bit input registers:

- preserved addend register \(a\) occupies qubits \(0\) through \(n-1\)
- overwritten addend register \(b\) occupies qubits \(n\) through \(2n-1\)
- the clean work qubit occupies qubit \(2n\)

The construction uses:

\[
N_{\mathrm{work}} = 1
\]

and the total logical register width is:

\[
N_{\mathrm{qubits}} = 2n + 1.
\]

The clean-work requirement is recorded separately from
`ResourceEstimate.ancilla_count`. The current circuit Intermediate
Representation (IR) does not retain qubit-role metadata, so the generic
resource estimator reports an ancilla count of zero.

## Results

| Register bits | Clean work qubits | Logical qubits | Gates | T gates | CNOT gates | Toffoli gates | Serial depth | Parallel depth |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 5 | 3 | 0 | 2 | 1 | 3 | 2 |
| 3 | 1 | 7 | 18 | 0 | 12 | 6 | 18 | 16 |
| 4 | 1 | 9 | 24 | 0 | 16 | 8 | 24 | 21 |
| 8 | 1 | 17 | 48 | 0 | 32 | 16 | 48 | 41 |
| 16 | 1 | 33 | 96 | 0 | 64 | 32 | 96 | 81 |

## Scaling

For \(n \geq 3\), the benchmark confirms:

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

and

\[
N_{\mathrm{gates}} = 6n.
\]

The serial depth is:

\[
D_{\mathrm{serial}} = 6n.
\]

The dependency-preserving parallel depth reported by the current estimator is:

\[
D_{\mathrm{parallel}} = 5n + 1.
\]

The \(n = 2\) row is a compact specialized implementation, not the general
Cuccaro majority/unmajority-and-add sequence. It is therefore reported in the
table but excluded from the asymptotic scaling formulas above.

## Interpretation

The benchmark treats Toffoli as a primitive logical gate. Consequently:

- T-count is zero
- Toffoli decomposition cost is not included
- T-depth is not estimated

These results describe the implemented high-level circuit construction, not
its eventual Clifford+T or physical fault-tolerant cost.

## Limitations

The benchmark does not include:

- carry-in or carry-out variants
- subtraction
- controlled addition
- modular reduction
- multiplication
- Toffoli decomposition into Clifford+T
- T-depth
- topology or routing
- gate durations
- measurement or feedforward
- physical error-correction resources
- alternative space-depth tradeoffs
