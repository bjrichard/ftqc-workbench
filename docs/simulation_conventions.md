# Simulation conventions

## Purpose

This document defines the simulation conventions used by the Fault-Tolerant Quantum Computing (FTQC) workbench.

These conventions control how basis states, statevectors, gate matrices, circuit unitaries, and equivalence checks are interpreted. They must remain explicit because different textbooks and quantum software libraries use different qubit-ordering conventions.

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

A test is not sufficient if it only checks matrix shape. Tests should also check at least a few basis-state actions, especially for controlled gates.

For example, tests for `CNOT` on qubits `(0, 1)` should verify that:

```text
|01> -> |11>
|11> -> |01>
```

under the interpretation:

```text
|q1 q0>
```

## Global phase convention

Global phase is expected to be ignored for unitary equivalence checks.

This means two unitaries `U` and `V` should be considered equivalent if there exists a phase `phi` such that:

```text
U = exp(i * phi) * V
```

This convention must be implemented and tested when unitary equivalence checking is added.

## Current limitations

The current simulation convention does not yet define behavior for:

- measurements
- feedforward
- classical control
- mid-circuit measurement
- noisy channels
- density matrices
- hardware topology
- routing or swap insertion

The current simulator should be treated as an exact small-circuit simulator for unitary logical circuits only.

## Implementation rule

When adding simulation code, do not infer qubit ordering from visual ket notation alone.

Always use the explicit index rule:

```text
index = q0 * 2^0 + q1 * 2^1 + ... + q_{n-1} * 2^{n-1}
```

This rule is the source of truth for basis-state indexing.
