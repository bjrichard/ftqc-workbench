# Week 3 log — Resource estimation foundation

## Week 3 objective

Build the first layer of the resource estimation system: immutable resource estimate objects and a simple logical resource estimator for circuit-level counts.

By the end of the week, the repo supports basic logical resource estimates for circuits, including total gate count, T-count, controlled-NOT count, controlled-Z count, ancilla count, and a simple serial depth estimate.

## Scope for this week

In scope:

- ResourceEstimate data model
- ResourceEstimator service object
- logical gate counting
- T-count
- controlled-NOT count
- controlled-Z count
- ancilla count placeholder
- serial depth estimate
- resource model documentation
- unit tests

Out of scope:

- physical qubit estimation
- surface-code distance
- magic-state factory modeling
- routing-aware depth
- parallelized depth
- scheduling
- hardware topology
- noise-aware resource estimates
- fault-tolerant decomposition

## Completed work

### Day 1 — ResourceEstimate model

Implemented an immutable `ResourceEstimate` object for scalar logical resource counts.

The model validates:

- total gate count
- T-count
- controlled-NOT count
- controlled-Z count
- ancilla count
- optional depth

Validation rejects:

- non-integer counts
- negative counts
- non-integer depth values
- negative depth values

Completed commit:

```bash
feat(resources): add resource estimate model
```

### Day 2 — ResourceEstimator gate counts

Implemented `ResourceEstimator` as the computation object that estimates logical resources from a `Circuit`.

The estimator currently counts:

- total gates
- T gates
- controlled-NOT gates
- controlled-Z gates

It also sets:

- `ancilla_count = 0`
- `depth = None` before the serial depth model was added

Completed commit:

```bash
feat(resources): add logical resource estimator
```

### Day 3 — Serial circuit depth

Updated `ResourceEstimator` so `depth` is a serial circuit depth estimate.

Current rule:

```python
depth = len(circuit)
```

This means each operation contributes one sequential layer.

This is not parallelized circuit depth.

Completed commit:

```bash
feat(resources): add serial circuit depth estimate
```

### Day 4 — Resource model documentation

Updated `docs/resource_model.md` to define the Week 3 logical resource model.

The documentation now explains:

- current circuit Intermediate Representation conventions
- primitive logical gate assumptions
- logical resource fields
- total gate count
- T-count
- controlled-NOT count
- controlled-Z count
- ancilla-count convention
- serial depth convention
- current non-goals and limitations

Completed commit:

```bash
docs(resources): define week 3 resource model
```

### Day 5 — Week 3 cleanup and completion log

Reviewed resource package structure, tests, documentation, and public imports.

Completed this Week 3 log.

Expected commit:

```bash
docs(plan): add week 3 completion log
```

## Current package state

The resource package now exposes:

```python
from qc_compiler.resources import ResourceEstimate, ResourceEstimator
```

`ResourceEstimate` is the immutable result object.

`ResourceEstimator` is the service object that computes a `ResourceEstimate` from a `Circuit`.

## Current estimator behavior

For a circuit with `n` operations:

```python
gate_count = n
depth = n
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

The Week 3 estimator is a logical bookkeeping estimator only.

It does not estimate:

- physical qubits
- surface-code distance
- magic-state factories
- distillation cost
- physical runtime
- routing overhead
- swap overhead
- scheduled depth
- parallelized depth
- T-depth
- measurement cost
- feedforward latency
- noise-aware cost

## Tests added or updated

Week 3 added tests for:

- valid `ResourceEstimate` construction
- invalid count types
- negative counts
- optional depth validation
- immutability
- public package imports
- empty circuit estimates
- non-empty circuit gate counts
- T-count
- controlled-NOT count
- controlled-Z count
- ancilla-count convention
- serial depth
- non-Circuit input rejection

## Completion criteria

Week 3 is complete because:

- `ResourceEstimate` is implemented and tested.
- `ResourceEstimator` is implemented and tested.
- The estimator returns logical gate counts.
- The estimator returns serial circuit depth.
- Resource model assumptions are documented.
- Public resource imports work.
- The full test suite passes.
- Week 3 changes are committed and pushed.

## Week 3 result

Week 3 successfully added the first usable logical resource estimation layer to the Fault-Tolerant Quantum Computing (FTQC) workbench.
