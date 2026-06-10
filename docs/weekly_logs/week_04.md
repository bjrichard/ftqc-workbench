# Week 4 log — Resource-estimation refinement

## Week 4 objective

Extend the logical resource-estimation layer beyond simple gate counting by adding circuit-width accounting and a first parallelized depth model.

By the end of the week, the repo supports logical qubit count, serial depth, greedy order-preserving parallelized depth, and documentation explaining the difference between these quantities.

## Scope for this week

In scope:

- logical qubit count
- serial depth convention
- greedy order-preserving parallelized depth
- standalone parallel depth helper
- integration of parallel depth into `ResourceEstimate`
- integration of parallel depth into `ResourceEstimator`
- resource model documentation
- unit tests

Out of scope:

- physical qubit estimation
- surface-code distance
- magic-state factory modeling
- routing-aware depth
- hardware-aware scheduling
- gate commutation analysis
- global circuit rescheduling
- optimal depth under arbitrary circuit rewrites
- noise-aware resource estimates
- fault-tolerant decomposition

## Design decisions

- `logical_qubit_count` is defined as the number of logical qubit slots represented by the circuit.
- Current rule: `logical_qubit_count = circuit.num_qubits`.
- `depth` remains the serial circuit depth estimate.
- Current rule: `depth = len(circuit)`.
- `parallel_depth` is added as a separate field rather than redefining `depth`.
- Current rule: `parallel_depth = estimate_parallel_depth(circuit)`.
- `estimate_parallel_depth` uses a greedy order-preserving layer assignment.
- The parallel depth model allows operations on disjoint qubits to share a layer.
- The parallel depth model does not commute, cancel, reorder, route, schedule globally, or optimize across equivalent circuits.

## Completed work

### Day 1 — Logical qubit count

Added `logical_qubit_count` to `ResourceEstimate`.

Updated validation so logical qubit count must be:

- an integer
- nonnegative

Updated `ResourceEstimator` so:

```python
logical_qubit_count = circuit.num_qubits
```

Updated tests for:

- valid `ResourceEstimate` construction
- non-integer logical qubit count rejection
- negative logical qubit count rejection
- empty circuit logical qubit count
- non-empty circuit logical qubit count

Completed commit:

```bash
feat(resources): add logical qubit count
```

### Day 2 — Parallel depth estimator helper

Added a standalone helper:

```python
estimate_parallel_depth(circuit)
```

The helper estimates greedy order-preserving parallelized circuit depth.

Algorithm:

1. Start with an empty list of layers.
2. Represent each layer as a set of occupied qubit indices.
3. Loop through operations in circuit order.
4. Convert each operation's qubits to a set for conflict checking.
5. Place the operation into the earliest layer whose occupied qubits are disjoint from the operation's qubits.
6. If no compatible layer exists, create a new layer.
7. Return the number of layers.

Added tests for:

- empty circuit depth
- single-operation depth
- disjoint single-qubit operations sharing a layer
- same-qubit operations requiring separate layers
- two-qubit gate conflicts
- reuse of later available layers
- non-Circuit input rejection
- public package import

Completed commit:

```bash
feat/resources): add parallel depth estimator
```

Completed commit:

```bash
feat(resources): add parallel depth estimator
```

### Day 3 — Parallel depth estimate integration

Added `parallel_depth` to `ResourceEstimate`.

Updated validation so parallel depth may be:

- a nonnegative integer
- `None`

Updated `ResourceEstimator` so:

```python
depth = len(circuit)
parallel_depth = estimate_parallel_depth(circuit)
```

This preserves the distinction between serial depth and parallelized depth.

Added tests for:

- valid `parallel_depth` storage
- omitted parallel depth
- non-integer parallel depth rejection
- negative parallel depth rejection
- empty circuit parallel depth
- non-empty circuit where serial depth and parallel depth differ

Completed commit:

```bash
feat(resources): add parallel depth estimate
```

### Day 4 — Resource model documentation

Updated `docs/resource_model.md` to document the Week 4 resource model.

The documentation now explains:

- logical qubit count
- serial depth
- greedy order-preserving parallelized depth
- `estimate_parallel_depth`
- the difference between `depth` and `parallel_depth`
- current limitations and non-goals

Completed commit:

```bash
docs(resources): document parallel depth model
```

### Day 5 — Week 4 cleanup and completion log

Reviewed Week 4 resource-estimation changes, documentation, and tests.

Completed this Week 4 log.

Expected commit:

```bash
docs(plan): add week 4 completion log
```

## Current package state

The resource package now exposes:

```python
from qc_compiler.resources import (
    ResourceEstimate,
    ResourceEstimator,
    estimate_parallel_depth,
)
```

`ResourceEstimate` is the immutable result object.

`ResourceEstimator` is the service object that computes a `ResourceEstimate` from a `Circuit`.

`estimate_parallel_depth` is a standalone helper for greedy order-preserving parallelized depth estimation.

## Current estimator behavior

For a circuit with `n` operations and `q` logical qubits:

```python
gate_count = n
logical_qubit_count = q
depth = n
parallel_depth = estimate_parallel_depth(circuit)
```

For primitive logical gates:

```python
t_count = number of T operations
cnot_count = number of controlled-NOT operations
cz_count = number of controlled-Z operations
```

Current ancilla convention:

```python
ancilla_count = 0
```

## Important limitations

The Week 4 estimator is still a logical bookkeeping estimator only.

It does not estimate:

- physical qubits
- surface-code distance
- code cycles
- magic-state factories
- distillation cost
- physical runtime
- routing overhead
- swap overhead
- hardware-aware scheduling
- gate commutation effects
- globally optimized depth
- T-depth
- measurement cost
- feedforward latency
- noise-aware cost

## Tests added or updated

Week 4 added or updated tests for:

- logical qubit count validation
- logical qubit count estimation
- standalone parallel depth estimation
- empty circuit parallel depth
- single-operation parallel depth
- disjoint operation layer sharing
- same-qubit operation conflicts
- two-qubit gate conflicts
- earliest compatible layer placement
- `parallel_depth` validation
- `parallel_depth` integration in `ResourceEstimator`
- public package imports

## Completion criteria

Week 4 is complete because:

- `logical_qubit_count` is implemented and tested.
- `estimate_parallel_depth` is implemented and tested.
- `parallel_depth` is implemented and tested.
- Serial depth and parallelized depth are represented separately.
- Resource model assumptions are documented.
- Public resource imports work.
- The full test suite passes.
- Week 4 changes are committed and pushed.

## Week 4 result

Week 4 refined the logical resource-estimation layer of the Fault-Tolerant Quantum Computing (FTQC) workbench by adding logical width and a first parallelized depth model while preserving clear boundaries around what is not yet modeled.
