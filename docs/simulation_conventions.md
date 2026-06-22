# Simulation conventions

## Purpose

This document defines the simulation conventions used by the Fault-Tolerant Quantum Computing (FTQC) workbench.

These conventions control how basis states, statevectors, gate matrices, circuit unitaries, and equivalence checks are interpreted. They must remain explicit because different textbooks and quantum software libraries use different qubit-ordering conventions.

## Statevector representation

An `n`-qubit statevector is represented as a one-dimensional, complex-valued NumPy array with length `2**n`.

Entry `statevector[j]` is the amplitude of computational basis state `|j>` under the little-endian indexing convention defined below.

Simulation functions return complex-valued arrays even when the supplied input statevector contains only real values.

## Statevector basis convention

The simulator uses little-endian statevector indexing.

This means qubit `0` is the least significant bit in the computational-basis index.

For an `n`-qubit computational basis state, the integer statevector index is defined as:

```text
index = q0 * 2^0 + q1 * 2^1 + ... + q_{n-1} * 2^{n-1}
```

where each `qj` is either `0` or `1`.

Equivalently, qubit `0` changes fastest as one moves through the statevector entries.

## Two-qubit basis ordering

For two qubits, the statevector entries are ordered by integer index as:

| Index | Binary index | Qubit values | Displayed ket |
|---:|---|---|---|
| 0 | `00` | `q1 = 0`, `q0 = 0` | `|00>` |
| 1 | `01` | `q1 = 0`, `q0 = 1` | `|01>` |
| 2 | `10` | `q1 = 1`, `q0 = 0` | `|10>` |
| 3 | `11` | `q1 = 1`, `q0 = 1` | `|11>` |

The displayed two-qubit ket is interpreted as:

```text
|q1 q0>
```

not as:

```text
|q0 q1>
```

Therefore:

```text
|01> means q1 = 0 and q0 = 1.
```

It does not mean that qubit `0` is in state `|0>` and qubit `1` is in state `|1>`.

## General basis-string convention

For `n` qubits, displayed computational basis strings are interpreted as:

```text
|q_{n-1} ... q2 q1 q0>
```

The rightmost bit corresponds to qubit `0`.

This convention matches the little-endian statevector index rule:

```text
index = q0 * 2^0 + q1 * 2^1 + ... + q_{n-1} * 2^{n-1}
```

## Operation qubit-order convention

For an operation written as:

```python
Operation(gate=gate, qubits=(q0, q1, ..., qk))
```

the tuple order defines the local matrix bit order.

The qubit at `operation.qubits[0]` corresponds to local bit position `0`, the qubit at `operation.qubits[1]` corresponds to local bit position `1`, and so on.

The local basis index is therefore:

```text
local_index =
    bit(q0) * 2^0
    + bit(q1) * 2^1
    + ...
    + bit(qk) * 2^k
```

This rule applies independently of whether the selected full-register qubits are adjacent.

Changing the order of the qubit tuple changes how the local gate matrix is embedded into the full statevector.

## Single-qubit gate convention

A single-qubit gate applied to qubit `k` acts on bit `qk` in the little-endian computational basis.

For example, applying `X` to qubit `0` in a two-qubit state flips the rightmost bit:

```text
|00> -> |01>
|01> -> |00>
|10> -> |11>
|11> -> |10>
```

Applying `X` to qubit `1` flips the leftmost bit:

```text
|00> -> |10>
|01> -> |11>
|10> -> |00>
|11> -> |01>
```

## Controlled-NOT convention

The circuit Intermediate Representation (IR) uses the convention:

```python
Operation(gate=CNOT, qubits=(control, target))
```

For `CNOT` on qubits `(0, 1)`, qubit `0` is the control and qubit `1` is the target.

Using the little-endian basis interpretation `|q1 q0>`, the action is:

```text
|00> -> |00>
|01> -> |11>
|10> -> |10>
|11> -> |01>
```

because the target qubit `q1` is flipped when the control qubit `q0` equals `1`.

In the two-qubit basis order:

```text
|00>, |01>, |10>, |11>
```

this corresponds to the matrix:

```text
[[1, 0, 0, 0],
 [0, 0, 0, 1],
 [0, 0, 1, 0],
 [0, 1, 0, 0]]
```

This differs from the matrix one would write if the two-qubit ket were interpreted as `|q0 q1>`.

## Controlled-Z convention

The circuit Intermediate Representation (IR) uses the convention:

```python
Operation(gate=CZ, qubits=(qubit_0, qubit_1))
```

The controlled-Z (CZ) gate is symmetric in its two qubits, so the qubit order does not change the logical action.

For two qubits, the gate applies a phase of `-1` only to the state where both qubits are `1`:

```text
|00> -> |00>
|01> -> |01>
|10> -> |10>
|11> -> -|11>
```

In the two-qubit basis order:

```text
|00>, |01>, |10>, |11>
```

this corresponds to the matrix:

```text
[[1, 0, 0,  0],
 [0, 1, 0,  0],
 [0, 0, 1,  0],
 [0, 0, 0, -1]]
```

## Matrix and simulator consistency rule

Primitive gate matrices, statevector simulation, circuit-to-unitary construction, and equivalence checking must all use the same little-endian convention.

A test is not sufficient if it only checks matrix shape. Tests should also check basis-state actions, especially for controlled gates and nonadjacent qubits.

For example, tests for `CNOT` on qubits `(0, 1)` should verify that:

```text
|01> -> |11>
|11> -> |01>
```

under the interpretation:

```text
|q1 q0>
```

## Circuit-unitary convention

For an `n`-qubit circuit, the represented unitary has shape:

```text
(2**n, 2**n)
```

Column `j` is the final statevector produced by simulating the circuit from computational basis state `|j>`:

```text
U[:, j] = simulate_statevector(circuit, initial_statevector=|j>)
```

Equivalently:

```text
U |j> = column j of U
```

The basis-state index `j` follows the same little-endian convention used by the statevector simulator.

Circuit operations are applied in the order stored in `circuit.operations`.

## Global phase convention

Global phase is ignored for unitary and circuit equivalence checks.

Two unitaries `U` and `V` are considered equivalent if there exists a real phase `phi` such that:

```text
U = exp(i * phi) * V
```

Equivalently, they may differ by one complex scalar with unit magnitude.

The equivalence implementation selects a nonzero reference entry, infers the candidate phase from the ratio of corresponding entries, verifies that the phase has unit magnitude, and checks that the same phase relates the complete matrices within numerical tolerance.

## Mutation and ownership convention

Simulation functions do not mutate statevectors supplied by the caller.

- `get_gate_matrix` returns a copy of the requested primitive gate matrix.
- `apply_operation_to_statevector` returns a newly allocated statevector.
- `simulate_statevector` copies a supplied initial statevector before applying circuit operations.
- `circuit_to_unitary` constructs and returns a new complex matrix.

Callers may therefore retain and reuse supplied arrays without simulation functions modifying them in place.

## Current limitations

The current simulation convention does not define behavior for:

- measurements
- feedforward
- classical control
- mid-circuit measurement
- noisy channels
- density matrices
- hardware topology
- routing or swap insertion

The current simulator should be treated as an exact small-circuit simulator for unitary logical circuits only.

It is intended as a correctness and verification reference, not as a scalable high-performance simulation backend.

## Implementation rule

When adding simulation code, do not infer qubit ordering from visual ket notation alone.

Always use the explicit index rule:

```text
index = q0 * 2^0 + q1 * 2^1 + ... + q_{n-1} * 2^{n-1}
```

This rule is the source of truth for basis-state indexing.

## References

1. McGuffin, Robert, and Ikeda, “How to Write a Simulator for Quantum Circuits from Scratch: A Tutorial,” arXiv:2506.08142, 2025.
2. Jones et al., “QuEST and High Performance Simulation of Quantum Computers,” arXiv:1802.08032.
3. Smelyanskiy et al., “qHiPSTER: The Quantum High Performance Software Testing Environment,” arXiv:1601.07195.
4. Guerreschi et al., “Intel Quantum Simulator: A Cloud-Ready High-Performance Simulator of Quantum Circuits,” arXiv:2001.10554.
5. IBM Quantum documentation, “Bit ordering.”
6. Google Quantum AI documentation, `qsim`.
7. Isakov et al., “Simulations of Quantum Circuits with Approximate Noise Using qsim and Cirq,” arXiv:2111.02396.
