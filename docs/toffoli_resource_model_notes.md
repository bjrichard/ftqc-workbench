# Toffoli resource model notes

## Purpose

This note defines how the project should distinguish primitive logical resource
estimates from expanded logical resource estimates.

The immediate motivation is that both major reversible primitive families
implemented so far rely heavily on Toffoli gates:

- clean-ancilla multi-controlled Pauli-X
- Cuccaro-style in-place modular adder

The current resource estimator treats Toffoli as a primitive logical gate.
That is useful for inspecting high-level circuit structure, but incomplete for
fault-tolerant quantum computing resource analysis.

## Current model

The current `ResourceEstimator` reports resource counts directly from the
circuit Intermediate Representation (IR).

For a circuit containing Toffoli operations, the estimator currently reports:

- `toffoli_count`: number of primitive Toffoli operations
- `t_count`: number of explicit primitive T gates in the circuit
- `cnot_count`: number of explicit primitive Controlled-NOT (CNOT) gates
- `gate_count`: number of operations in the circuit
- `depth`: serial operation count
- `parallel_depth`: dependency-preserving parallel depth

Under this model, Toffoli gates do not contribute to `t_count` unless they have
already been decomposed into Clifford+T gates in the circuit itself.

This is intentional for the primitive model. It allows benchmark tables to
describe the high-level circuit construction without silently assuming a
particular decomposition.

## Problem

For fault-tolerant quantum computing (FTQC), Toffoli gates are usually not
treated as native free operations.

A resource table that reports many Toffoli gates but zero T gates is therefore
easy to misread. The zero T-count means:

```text
No explicit T gates appear in the current circuit IR.
```

It does not mean:

```text
The circuit has zero T cost under a Clifford+T implementation.
```

The benchmark documentation currently explains this limitation, but the
resource model should eventually make the distinction explicit in code.

## Proposed model split

The project should maintain two resource-estimate layers.

### Primitive logical estimate

The primitive estimate counts exactly what appears in the circuit IR.

This estimate answers:

```text
What high-level logical operations did the builder emit?
```

It should continue to report:

- primitive gate count
- primitive CNOT count
- primitive Toffoli count
- explicit primitive T count
- logical qubit count
- serial depth
- dependency-preserving parallel depth

This estimate should not silently expand Toffoli gates.

### Expanded logical estimate

The expanded estimate analytically accounts for selected composite gate costs
without mutating the circuit.

This estimate answers:

```text
What would the logical resource counts be under a stated expansion convention?
```

The first expansion convention should account for Toffoli gates in terms of
T-count.

## First Toffoli expansion convention

The first expanded estimate should use the convention:

\[
N_T^{\mathrm{expanded}}
=
N_T^{\mathrm{primitive}}
+
7N_{\mathrm{Toffoli}}.
\]

That is:

```text
1 primitive Toffoli contributes 7 T gates.
```

This convention is simple, explicit, and useful for first-order comparison.

The expanded estimate should keep the primitive Toffoli count visible. It
should not erase the fact that the original circuit was expressed using
Toffoli gates.

## What not to implement yet

The first expanded model should not yet include:

- actual circuit decomposition
- T-depth
- Clifford count
- Hadamard/S/phase-gate accounting
- relative-phase Toffoli variants
- dirty-ancilla Toffoli variants
- measurement-assisted decompositions
- magic-state distillation cost
- physical qubit estimates
- code-distance estimates
- topology-aware routing
- hardware-specific timing assumptions

These require additional conventions and would make the first resource-model
extension less clear.

## Proposed API direction

The current `ResourceEstimate` should remain the primitive logical estimate.

Add a separate expanded estimate rather than changing the meaning of existing
fields.

A possible future dataclass is:

```python
@dataclass(frozen=True)
class ExpandedResourceEstimate:
    primitive: ResourceEstimate
    expanded_t_count: int
    toffoli_t_cost: int
    toffoli_expansion: str
```

The first implementation could expose a method such as:

```python
ResourceEstimator().estimate_with_toffoli_expansion(
    circuit,
    toffoli_t_cost=7,
)
```

or a separate helper function such as:

```python
estimate_toffoli_expanded_resources(
    circuit,
    *,
    toffoli_t_cost: int = 7,
) -> ExpandedResourceEstimate
```

The separate helper function is probably the better first implementation
because it avoids expanding the responsibility of `ResourceEstimator` too
quickly.

## Testing strategy

The tests should verify that the expanded estimate:

- preserves the original primitive estimate
- reports `expanded_t_count = primitive_t_count + 7 * toffoli_count`
- works for circuits with zero Toffoli gates
- works for circuits with only Toffoli gates
- works for mixed CNOT, T, and Toffoli circuits
- rejects invalid Toffoli T-cost conventions, such as non-integers, Booleans,
  zero, or negative values

The first tests should use small hand-built circuits, not the large benchmark
circuits.

## Impact on existing benchmarks

The existing multi-controlled Pauli-X and Cuccaro adder benchmark tables should
remain valid as primitive logical resource tables.

Later benchmark documentation can add an interpretation row or companion table
for expanded T-count.

For example, the Cuccaro adder currently has, for `n >= 3`:

\[
N_{\mathrm{Toffoli}} = 2n.
\]

Under the first Toffoli expansion convention, this implies:

\[
N_T^{\mathrm{expanded}} = 14n.
\]

The multi-controlled Pauli-X construction has, for `k >= 2`:

\[
N_{\mathrm{Toffoli}} = 2k - 3.
\]

Under the same convention, this implies:

\[
N_T^{\mathrm{expanded}} = 7(2k - 3).
\]

These formulas should be documented only after the expanded estimate API is
implemented and tested.
