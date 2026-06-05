# Resource model

## Status

This document records the current logical resource-model assumptions for the Fault-Tolerant Quantum Computing (FTQC) workbench.

As of Week 1, the project has only implemented the basic circuit Intermediate Representation (IR). A circuit IR is the internal data model used to represent quantum circuits before later steps such as resource estimation, simulation, verification, or optimization.

Resource counting begins in Week 3.

## Circuit IR conventions

Qubits are represented by zero-based integer indices.

Examples:

- qubit `0` is the first qubit
- qubit `1` is the second qubit
- a two-qubit circuit has valid qubit indices `0` and `1`

The core circuit IR objects are:

- `Gate`
- `Operation`
- `Circuit`

`Gate` represents an abstract reusable logical gate definition. It stores:

- `name`
- `arity`

`Operation` binds a `Gate` to concrete qubit indices.

Example:

```python
Operation(gate=CNOT, qubits=(0, 1))
```

For multi-qubit gates, qubit order follows the gate convention.

Current conventions:

- `CNOT`: `(control, target)`
- `CZ`: `(qubit_0, qubit_1)`
- `TOFFOLI`: `(control_0, control_1, target)`

`Circuit` stores:

- a fixed number of qubits
- an ordered tuple of operations

Appending an operation returns a new circuit rather than mutating the existing circuit.

## Current logical gate set

The current primitive logical gate library contains:

| Gate | Arity |
|---|---:|
| `I` | 1 |
| `X` | 1 |
| `Y` | 1 |
| `Z` | 1 |
| `H` | 1 |
| `S` | 1 |
| `T` | 1 |
| `CNOT` | 2 |
| `CZ` | 2 |
| `TOFFOLI` | 3 |

## Clifford+T assumptions

The intended logical gate set is Clifford+T.

For now, the project defines gate names and arities only. It does not yet attach Clifford or T-gate metadata to gates.

Expected future classification:

| Gate | Expected class |
|---|---|
| `I` | Clifford |
| `X` | Clifford |
| `Y` | Clifford |
| `Z` | Clifford |
| `H` | Clifford |
| `S` | Clifford |
| `CNOT` | Clifford |
| `CZ` | Clifford |
| `T` | non-Clifford |
| `TOFFOLI` | primitive placeholder; later decomposed or counted according to an explicit convention |

## Resource counting status

Resource counting is not implemented in Week 1.

Week 3 will define and test:

- gate count
- T-count
- controlled-NOT and controlled-Z count
- simple depth estimate
- ancilla-count convention

Until Week 3, no code should claim to produce resource estimates.

## Current out-of-scope assumptions

The current implementation does not model:

- gate matrices
- exact simulation
- unitary equivalence
- reversible truth-table verification
- measurements
- feedforward
- classical control
- connectivity
- routing
- swap-gate overhead
- physical qubits
- surface-code costs
- magic-state factories
- T-depth

## Connectivity and routing

Connectivity is ignored in the first implementation.

Operations may act on any valid qubit indices in the circuit. No hardware topology, routing, or nearest-neighbor constraint is currently modeled.

## Measurement and feedforward

Measurements and feedforward are out of scope unless explicitly promoted later.

The current circuit IR represents unitary logical operations only.

## Ancilla convention

Ancilla accounting is not implemented yet.

Default future assumption:

- count clean ancillae only
- document any dirty-ancilla convention explicitly before using it

## Global phase

Global phase handling is not implemented yet.

Expected future convention:

- global phase is ignored for unitary equivalence checks

This convention must be tested and documented when equivalence checking is implemented.
