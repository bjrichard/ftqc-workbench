# Week 3 log — Resource estimation foundation

## Week 3 objective

Build the first layer of the resource estimation system: immutable resource estimate objects and a simple logical resource estimator for circuit-level counts.

By the end of the week, the repo should support basic resource estimates for circuits, including total gate count, T-count, controlled-NOT count, controlled-Z count, ancilla count, and a simple serial depth estimate.

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

## Design decisions

- ResourceEstimate represents an immutable result object.
- ResourceEstimator represents the computation that produces a ResourceEstimate from a Circuit.
- Total gate count is defined as the number of operations in the circuit.
- T-count counts operations whose gate is the primitive T gate.
- Controlled-NOT count counts operations whose gate is the primitive controlled-NOT gate.
- Controlled-Z count counts operations whose gate is the primitive controlled-Z gate.
- Ancilla count is set to 0 until the project introduces decompositions, workspace allocation, or fault-tolerant resource models.
- Depth is initially modeled as serial depth, where each operation contributes one layer.
- Serial depth is not parallelized circuit depth.

## Daily plan

### Day 1 — ResourceEstimate model

Add an immutable ResourceEstimate object with validation for nonnegative integer resource counts.

Expected commit:

```bash
feat(resources): add resource estimate model
```

### Day 2 — ResourceEstimator gate counts

Add a ResourceEstimator object that computes logical gate counts from a Circuit.

Expected commit:

```bash
feat(resources): add logical resource estimator
```

### Day 3 — Serial circuit depth

Add a simple serial depth estimate equal to the number of operations in the circuit.

Expected commit:

```bash
feat(resources): add serial circuit depth estimate
```

### Day 4 — Resource model documentation

Document the Week 3 resource model, including what is counted, what is assumed, and what is explicitly out of scope.

Expected commit:

```bash
docs(resources): define week 3 resource model
```

### Day 5 — Week 3 cleanup and completion log

Review tests, documentation, and public imports. Finalize the Week 3 log.

Expected commit:

```bash
docs(plan): add week 3 completion log
```

## Completion criteria

Week 3 is complete when:

- ResourceEstimate is implemented and tested.
- ResourceEstimator is implemented and tested.
- The estimator returns logical gate counts.
- The estimator returns serial circuit depth.
- Resource model assumptions are documented.
- The full test suite passes.
- Week 3 changes are committed and pushed.
