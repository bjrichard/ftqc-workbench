# Resource model

## Status

This document records the current logical resource-model assumptions for the Fault-Tolerant Quantum Computing (FTQC) workbench.

As of Week 4, the project has implemented:

- the basic circuit Intermediate Representation (IR)
- primitive logical gate definitions
- immutable circuit operations
- immutable resource estimate objects
- a basic logical resource estimator
- total gate counting
- T-gate counting
- controlled-NOT (CNOT) gate counting
- controlled-Z (CZ) gate counting
- logical qubit counting
- an ancilla-count convention
- a serial circuit depth estimate
- a greedy order-preserving parallelized circuit depth estimate

The current estimates are logical bookkeeping estimates. They are not physical resource estimates and should not be interpreted as surface-code cost estimates, hardware runtime estimates, or practical fault-tolerant execution estimates.

## Circuit Intermediate Representation conventions

The circuit Intermediate Representation (IR) is the internal data model used to represent quantum circuits before later steps such as resource estimation, simulation, verification, compilation, optimization, or hardware mapping.

Qubits are represented by zero-based integer indices.

Examples:

- qubit `0` is the first qubit
- qubit `1` is the second qubit
- a two-qubit circuit has valid qubit indices `0` and `1`

The core circuit Intermediate Representation (IR) objects are:

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

- controlled-NOT (CNOT): `(control, target)`
- controlled-Z (CZ): `(qubit_0, qubit_1)`
- Toffoli gate (`TOFFOLI`): `(control_0, control_1, target)`

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

## Current resource estimate object

Resource estimates are represented by `ResourceEstimate`.

A `ResourceEstimate` stores scalar logical resource counts:

- `gate_count`
- `t_count`
- `cnot_count`
- `cz_count`
- `logical_qubit_count`
- `ancilla_count`
- `depth`
- `parallel_depth`

The estimate object is immutable after construction.

## Current resource estimator

Logical resource estimates are computed by `ResourceEstimator`.

The current estimator accepts a `Circuit` and returns a `ResourceEstimate`.

Example:

```python
estimate = ResourceEstimator().estimate(circuit)
```

The estimator currently computes:

- total gate count
- T-gate count
- controlled-NOT (CNOT) gate count
- controlled-Z (CZ) gate count
- logical qubit count
- ancilla count
- serial circuit depth
- greedy order-preserving parallelized circuit depth

The estimator does not yet model decomposition, routing, scheduling, gate commutation, global depth optimization, measurement, feedforward, noise, or physical fault-tolerant overhead.

## Resource fields

### `gate_count`

`gate_count` is the total number of operations in the circuit.

Current rule:

```python
gate_count = len(circuit)
```

Each operation contributes one gate to the total count.

### `t_count`

`t_count` is the number of operations whose gate is the primitive `T` gate.

Current rule:

```python
t_count = number of operations where operation.gate == T
```

This is a logical T-count only. It does not yet include T gates introduced by decompositions.

### `cnot_count`

`cnot_count` is the number of operations whose gate is the primitive controlled-NOT (CNOT) gate.

Current rule:

```python
cnot_count = number of operations where operation.gate == CNOT
```

This is a logical controlled-NOT (CNOT) count only. It does not yet include controlled-NOT (CNOT) gates introduced by routing, decomposition, or compilation passes.

### `cz_count`

`cz_count` is the number of operations whose gate is the primitive controlled-Z (CZ) gate.

Current rule:

```python
cz_count = number of operations where operation.gate == CZ
```

This is a logical controlled-Z (CZ) count only. It does not yet include controlled-Z (CZ) gates introduced by routing, decomposition, or compilation passes.

### `logical_qubit_count`

`logical_qubit_count` is the number of logical qubit slots represented by the circuit.

Current rule:

```python
logical_qubit_count = circuit.num_qubits
```

This is a logical circuit-width estimate only. It is not a physical qubit estimate and does not include ancillas, syndrome-extraction qubits, routing resources, or magic-state factory qubits.

### `ancilla_count`

`ancilla_count` is currently set to zero.

Current rule:

```python
ancilla_count = 0
```

This is not a claim that fault-tolerant implementations require no ancillas. It means the current estimator does not yet model decompositions, workspace allocation, syndrome extraction, magic-state factories, or any other process that would introduce auxiliary qubits.

Future ancilla conventions must distinguish clean ancillas from dirty ancillas before nonzero ancilla estimates are introduced.

### `depth`

`depth` is currently a serial circuit depth estimate.

Current rule:

```python
depth = len(circuit)
```

Each operation contributes one sequential layer.

This is not parallelized circuit depth.

### `parallel_depth`

`parallel_depth` is currently a greedy order-preserving parallelized circuit depth estimate.

Current rule:

```python
parallel_depth = estimate_parallel_depth(circuit)
```

The helper function `estimate_parallel_depth` loops through operations in circuit order and places each operation into the earliest existing layer whose occupied qubits do not overlap with the operation's qubits. If no compatible layer exists, it creates a new layer.

This model allows operations on disjoint qubits to share a layer.

Example:

```python
circuit = (
    Circuit(num_qubits=2)
    .append_gate(gate=X, qubits=(0,))
    .append_gate(gate=Z, qubits=(1,))
    .append_gate(gate=CNOT, qubits=(0, 1))
)
```

For this circuit:

```python
depth = 3
parallel_depth = 2
```

The first two single-qubit operations can share one parallel layer. The controlled-NOT (CNOT) operation must occupy a later layer because it touches both qubits.

This is not a globally optimized scheduler. It does not commute gates, cancel gates, reorder operations, insert swaps, account for hardware topology, or optimize across alternative valid circuit representations.

## Example: empty circuit

For an empty two-qubit circuit:

```python
circuit = Circuit(num_qubits=2)
estimate = ResourceEstimator().estimate(circuit)
```

The expected estimate is:

```python
ResourceEstimate(
    gate_count=0,
    t_count=0,
    cnot_count=0,
    cz_count=0,
    logical_qubit_count=2,
    ancilla_count=0,
    depth=0,
    parallel_depth=0,
)
```

## Example: non-empty circuit

For the circuit:

```python
circuit = (
    Circuit(num_qubits=2)
    .append_gate(gate=T, qubits=(0,))
    .append_gate(gate=CNOT, qubits=(0, 1))
    .append_gate(gate=CZ, qubits=(0, 1))
    .append_gate(gate=X, qubits=(1,))
)
```

The expected estimate is:

```python
ResourceEstimate(
    gate_count=4,
    t_count=1,
    cnot_count=1,
    cz_count=1,
    logical_qubit_count=2,
    ancilla_count=0,
    depth=4,
    parallel_depth=3,
)
```

The serial depth is four because the circuit has four operations. The parallelized depth is three because the first `T` operation on qubit `0` and the final `X` operation on qubit `1` can occupy the same parallel layer under the current greedy order-preserving model.

## Connectivity and routing

Connectivity is ignored in the current implementation.

Operations may act on any valid qubit indices in the circuit. No hardware topology, routing, nearest-neighbor constraint, swap insertion, or movement cost is currently modeled.

## Measurement and feedforward

Measurements and feedforward are out of scope unless explicitly promoted later.

The current circuit Intermediate Representation (IR) represents unitary logical operations only.

## Ancilla convention

Ancilla accounting is currently implemented as a placeholder convention:

```python
ancilla_count = 0
```

Default future assumption:

- count clean ancillas only
- document any dirty-ancilla convention explicitly before using it
- distinguish logical ancillas from physical qubits
- distinguish circuit-level workspace from fault-tolerant syndrome-extraction resources

## Global phase

Global phase handling is not implemented yet.

Expected future convention:

- global phase is ignored for unitary equivalence checks

This convention must be tested and documented when equivalence checking is implemented.

## Explicit non-goals

The current resource model does not estimate:

- physical qubit count
- surface-code distance
- code cycles
- magic-state factory footprint
- magic-state factory throughput
- distillation cost
- measurement cost
- feedforward latency
- routing overhead
- swap overhead
- hardware topology constraints
- crosstalk
- calibration-dependent performance
- noise-aware resource costs
- wall-clock runtime
- scheduled depth
- T-depth
- Toffoli decomposition cost
- arbitrary gate synthesis cost
- gate commutation analysis
- global circuit rescheduling
- optimal depth under arbitrary circuit rewrites
- hardware-aware scheduling

## Interpretation

The current estimates are logical bookkeeping estimates, not fault-tolerant resource estimates.

They are useful for checking that the circuit Intermediate Representation (IR), primitive gate definitions, and estimator plumbing work correctly.

They are not yet sufficient for:

- comparing fault-tolerant architectures
- estimating hardware requirements
- estimating physical qubit counts
- estimating surface-code overhead
- estimating magic-state factory cost
- estimating execution time
- making claims about practical quantum advantage

## Near-term extensions

Likely next extensions include:

- Clifford+T decomposition counting
- T-depth
- simple routing-aware estimates
- primitive pass-based resource estimation
- resource estimates before and after compilation passes
- max-qubit-load diagnostics
- documentation examples comparing serial depth and parallelized depth
