# Resource model

## Status

This document records the current logical resource-model assumptions for the Fault-Tolerant Quantum Computing (FTQC) workbench.

As of Week 6, the project has implemented:

- the basic circuit Intermediate Representation (IR)
- primitive logical gate definitions
- immutable circuit operations
- immutable resource estimate objects
- a basic logical resource estimator
- total gate counting
- T-gate counting
- controlled-NOT (CNOT) gate counting
- controlled-Z (CZ) gate counting
- Toffoli-gate counting
- logical qubit counting
- an ancilla-count convention
- a serial circuit depth estimate
- a greedy parallelized circuit depth estimate

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
| `TOFFOLI` | primitive placeholder counted explicitly; later decomposed according to an explicit convention |

## Current resource estimate object

Resource estimates are represented by `ResourceEstimate`.

A `ResourceEstimate` stores scalar logical resource counts:

- `gate_count`
- `t_count`
- `cnot_count`
- `cz_count`
- `toffoli_count`
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
- Toffoli-gate count
- logical qubit count
- ancilla count
- serial circuit depth
- greedy parallelized circuit depth

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

This is a logical T-count only. It does not include T gates that would be introduced by decomposing higher-level gates such as Toffoli.

### `cnot_count`

`cnot_count` is the number of operations whose gate is the primitive controlled-NOT (CNOT) gate.

Current rule:

```python
cnot_count = number of operations where operation.gate == CNOT
```

This is a logical controlled-NOT (CNOT) count only. It does not include controlled-NOT (CNOT) gates introduced by routing, decomposition, or compilation passes.

### `cz_count`

`cz_count` is the number of operations whose gate is the primitive controlled-Z (CZ) gate.

Current rule:

```python
cz_count = number of operations where operation.gate == CZ
```

This is a logical controlled-Z (CZ) count only. It does not include controlled-Z (CZ) gates introduced by routing, decomposition, or compilation passes.

### `toffoli_count`

`toffoli_count` is the number of operations whose gate is the primitive `TOFFOLI` gate.

Current rule:

```python
toffoli_count = number of operations where operation.gate == TOFFOLI
```

The Toffoli count records logical Toffoli operations exactly as they appear in the circuit.

It does not convert Toffoli gates into:

- T gates,
- controlled-NOT (CNOT) gates,
- Clifford gates,
- relative-phase Toffoli gates,
- magic states,
- or fault-tolerant code cycles.

Those costs require an explicit decomposition and lower-level resource convention.

### `logical_qubit_count`

`logical_qubit_count` is the number of logical qubit slots represented by the circuit.

Current rule:

```python
logical_qubit_count = circuit.num_qubits
```

This is a logical circuit-width estimate only. It is not a physical qubit estimate.

Every qubit slot in the circuit contributes to this count, regardless of whether the qubit is used as data, target, control, or temporary workspace.

### `ancilla_count`

`ancilla_count` is currently set to zero.

Current rule:

```python
ancilla_count = 0
```

This is not a claim that the circuit contains no ancillas or that fault-tolerant implementations require no ancillas.

The current `Circuit` Intermediate Representation does not store qubit-role metadata. Once a builder returns a generic circuit, the estimator cannot determine which qubits were declared as clean ancillas, dirty ancillas, controls, targets, or ordinary data qubits.

Inferring ancilla roles from the operation pattern would be unreliable. Therefore, the estimator continues to report zero until ancilla information is represented explicitly.

Future ancilla conventions must distinguish:

- clean ancillas,
- dirty or borrowed ancillas,
- circuit-level workspace,
- decomposition ancillas,
- syndrome-extraction qubits,
- and physical fault-tolerant resources.

### `depth`

`depth` is currently a serial circuit depth estimate.

Current rule:

```python
depth = len(circuit)
```

Each operation contributes one sequential layer.

This is not parallelized circuit depth.

### `parallel_depth`

`parallel_depth` is a dependency-preserving parallel circuit depth estimate.

Current rule:

```python
parallel_depth = estimate_parallel_depth(circuit)
```

The helper tracks the latest execution layer used by each qubit. For every operation, it assigns the operation to one layer after the latest layer occupied by any qubit in that operation:

```python
operation_layer = (
    max(
        last_layer_by_qubit[qubit]
        for qubit in operation.qubits
    )
    + 1
)
```

It then records that layer for every qubit touched by the operation.

This preserves the order of operations that share any qubit while allowing operations on disjoint qubits to occupy the same layer.

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

The first two single-qubit operations can share layer 1 because they act on disjoint qubits. The controlled-NOT (CNOT) operation occupies layer 2 because it acts on both qubits after their preceding operations.

Dependency propagation can occur through a chain of shared qubits. For example:

```text
O1 acts on q0 and q1
O2 acts on q1 and q2
O3 acts on q2 and q3
```

The operations must occupy three successive layers because `O2` follows `O1` on `q1`, and `O3` follows `O2` on `q2`.

The implementation runs in time proportional to the total number of qubit operands across all operations:

\[
O\left(\sum_i a_i\right),
\]

where \(a_i\) is the arity of operation \(i\). For a fixed-arity gate set, this is linear in the number of operations. The implementation stores one latest-layer value per circuit qubit.

This is not a globally optimized scheduler. It does not:

- commute gates,
- cancel gates,
- insert swaps,
- account for hardware topology,
- model gate duration,
- optimize across algebraically equivalent circuit representations,
- or find a minimum-depth schedule under arbitrary circuit rewrites.

It estimates parallel depth for the circuit exactly as ordered, subject to per-qubit dependencies.

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
    toffoli_count=0,
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
    toffoli_count=0,
    logical_qubit_count=2,
    ancilla_count=0,
    depth=4,
    parallel_depth=3,
)
```

The serial depth is four because the circuit has four operations.

## Example: multi-controlled X circuit

Consider a four-controlled Pauli-X circuit constructed with:

```python
circuit = build_multi_controlled_x(
    controls=(0, 1, 2, 3),
    target=4,
    ancillas=(5, 6),
    num_qubits=7,
)
```

The clean-ancilla ladder contains five Toffoli operations:

```python
estimate = ResourceEstimator().estimate(circuit)
```

The expected logical counts are:

```python
estimate.gate_count == 5
estimate.toffoli_count == 5
estimate.t_count == 0
estimate.cnot_count == 0
estimate.cz_count == 0
estimate.logical_qubit_count == 7
estimate.ancilla_count == 0
estimate.depth == 5
```

For \(m \geq 3\) controls, the implemented ladder has:

\[
N_{\text{Toffoli}} = 2m - 3.
\]

The builder itself requires \(m-2\) clean ancillas, but the estimator still reports:

```python
ancilla_count = 0
```

because ancilla roles are not retained in the generic circuit representation.

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

Default future assumptions:

- count clean ancillas only when roles are represented explicitly,
- document any dirty-ancilla convention before using it,
- distinguish logical ancillas from physical qubits,
- distinguish circuit-level workspace from fault-tolerant syndrome-extraction resources,
- and do not infer ancilla roles from gate patterns.

## Global phase

Global phase is ignored for unitary and circuit equivalence checks.

Two unitaries \(U\) and \(V\) are considered equivalent when there exists a phase \(\phi\) such that

\[
U = e^{i\phi}V.
\]

This convention belongs to verification rather than resource estimation.

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

They are useful for:

- checking circuit Intermediate Representation behavior,
- tracking primitive logical gates,
- comparing circuits before and after explicit transformations,
- validating synthesized gate counts,
- and confirming expected scaling for reference constructions.

They are not sufficient for:

- comparing fault-tolerant architectures,
- estimating hardware requirements,
- estimating physical qubit counts,
- estimating surface-code overhead,
- estimating magic-state factory cost,
- estimating execution time,
- or making claims about practical quantum advantage.

## Near-term extensions

Likely next extensions include:

- explicit ancilla-role metadata
- Clifford+T decomposition counting
- T-depth
- dependency-aware scheduling
- simple routing-aware estimates
- primitive pass-based resource estimation
- resource estimates before and after compilation passes
- max-qubit-load diagnostics
- documentation examples comparing serial and parallel depth
