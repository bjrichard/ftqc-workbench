# Week 6 log — Reversible circuit construction and resource integration

## Week 6 objective

Extend the Fault-Tolerant Quantum Computing (FTQC) workbench with exact reversible-circuit simulation, basis-state permutation extraction, clean-ancilla multi-controlled Pauli-X construction, and logical resource-model integration.

By the end of the week, the repository supports reversible computational-basis simulation, multi-controlled X synthesis from Controlled-NOT (CNOT) and Toffoli gates, exhaustive clean-ancilla verification, explicit Toffoli counting, and dependency-preserving parallel-depth estimation.

## Scope for this week

In scope:

- computational-basis simulation
- identity, Pauli-X, CNOT, and Toffoli support
- basis-state permutation extraction
- clean-ancilla multi-controlled Pauli-X construction
- structural and exhaustive behavioral verification
- Toffoli matrix and unitary coverage
- logical Toffoli counting
- dependency-preserving parallel depth
- supporting documentation

Out of scope:

- circuit composition
- variable-arity gate abstractions
- dirty-ancilla synthesis
- relative-phase Toffoli synthesis
- Toffoli decomposition into Clifford+T gates
- T-depth
- routing and topology
- measurement and feedforward
- physical fault-tolerant resource estimation

## Design decisions

- Reversible basis-state simulation remains separate from statevector simulation.
- Qubit `0` remains the least significant bit under the project’s little-endian convention.
- Multi-controlled Pauli-X is implemented as a circuit builder rather than as a new variable-arity gate.
- One control produces CNOT.
- Two controls produce Toffoli.
- Three or more controls use a clean-ancilla compute–use–uncompute ladder.
- The ladder requires exactly \(m - 2\) clean ancillas and \(2m - 3\) Toffoli gates for \(m \geq 3\).
- Behavioral verification is restricted to inputs where declared ancillas begin in \(|0\rangle\).
- Toffoli gates are counted explicitly as logical primitives without assigning an implicit Clifford+T cost.
- `ancilla_count` remains zero because the current circuit Intermediate Representation (IR) does not retain qubit-role metadata.
- Parallel depth preserves per-qubit operation order while allowing disjoint operations to share a layer.
- Circuit composition remains deferred.

## Completed work

### Day 1 — Computational-basis simulation

Implemented `simulate_basis_state` for reversible circuits.

Supported gates:

- identity
- Pauli-X
- CNOT
- Toffoli

Added validation for:

- non-`Circuit` inputs
- Boolean and non-integer basis indices
- negative basis indices
- out-of-range basis indices
- unsupported gates

Added tests for standard, reordered, and nonadjacent qubit roles.

### Day 2 — Basis-state permutation extraction

Implemented:

```python
basis_state_permutation(circuit)
```

The function simulates every computational-basis input and returns the induced permutation as an immutable tuple.

Added tests for:

- empty circuits
- Pauli-X
- CNOT
- Toffoli
- reordered Toffoli roles
- invalid inputs

### Day 3 — Multi-controlled Pauli-X builder

Implemented:

```python
build_multi_controlled_x(
    controls,
    target,
    ancillas=(),
    *,
    num_qubits,
)
```

The builder handles:

- one control with CNOT
- two controls with Toffoli
- three or more controls with a clean-ancilla Toffoli ladder

Added strict validation for control, target, ancilla, and register indices.

Added structural tests for the generated operation sequences.

Added exhaustive basis-state verification over the clean-ancilla input subspace.

Added supporting documentation for:

- ancilla semantics
- compute–use–uncompute
- clean versus dirty ancillas
- resource counts
- verification strategy
- compiler and fault-tolerant considerations

### Day 4 — Resource-model integration

Extended `ResourceEstimate` and `ResourceEstimator` with explicit logical Toffoli counting.

Added resource tests for synthesized multi-controlled X circuits.

Replaced the previous layer-packing depth logic with dependency-preserving parallel-depth estimation based on the latest layer used by each qubit.

The updated depth model:

- preserves the order of operations sharing a qubit
- allows disjoint operations to share a layer
- propagates dependencies through chains of shared qubits
- runs in linear time for a fixed-arity gate set

Updated `docs/resource_model.md` to document the new Toffoli count and depth behavior.

### Day 5 — Integration review and closeout

Ran the full test suite successfully.

Reviewed public imports and integration across:

- basis-state simulation
- basis-state permutations
- Toffoli matrix and statevector support
- Toffoli unitary construction
- multi-controlled X synthesis
- exhaustive clean-ancilla verification
- resource counting
- parallel-depth estimation

Ran Ruff.

Ruff reports:

```text
E741 Ambiguous variable name: `I`
```

for the public identity-gate symbol:

```python
I = Gate(name="I", arity=1)
```

No code change was made. `I` is the conventional symbol for the identity gate and is retained intentionally.

## Current package capabilities

The project now supports:

- exact statevector simulation for small circuits
- exact reversible basis-state simulation
- circuit-to-unitary construction
- equivalence checking up to global phase
- basis-state permutation extraction
- clean-ancilla multi-controlled X construction
- logical Toffoli counting
- serial depth
- dependency-preserving parallel depth

## Tests added or extended

Week 6 added or extended tests for:

- reversible basis-state simulation
- basis-state permutations
- reordered and nonadjacent Toffoli roles
- multi-controlled X structure
- exhaustive clean-ancilla behavior
- Toffoli matrix retrieval
- Toffoli statevector application
- Toffoli unitary construction
- Toffoli resource counting
- multi-controlled X resource counts
- dependency-preserving parallel depth

## Documentation added or extended

Week 6 added or extended:

- multi-controlled X and ancilla synthesis notes
- resource-model documentation
- simulation and verification coverage notes
- this Week 6 completion log

## Important limitations

The current implementation does not yet support:

- circuit composition
- ancilla-role metadata
- dirty or borrowed ancillas
- relative-phase constructions
- hardware-aware synthesis
- Toffoli decomposition cost
- T-depth
- routing
- topology-aware scheduling
- physical fault-tolerant resource estimation

## End-of-week review

1. What was completed?
   - Reversible basis-state simulation, basis-state permutations, clean-ancilla multi-controlled X synthesis, exhaustive verification, Toffoli counting, and dependency-preserving parallel depth.

2. What is behind schedule?
   - Nothing material.

3. What should be cut?
   - Nothing.

4. What should move to backlog?
   - Circuit composition, ancilla metadata, alternative synthesis strategies, and lower-level fault-tolerant cost models.

5. What is next week’s main deliverable?
   - Resume the project roadmap from the next planned compiler or synthesis objective while preserving the new verification and resource-analysis foundations.

6. Did any result suggest a publishable angle?
   - No. The work remains a portfolio-quality software and compiler foundation.

7. Do any scope-cut triggers apply?
   - No.

## Week 6 definition of done

Week 6 is complete because:

- reversible basis-state simulation is implemented and tested
- basis-state permutation extraction is implemented and tested
- multi-controlled X synthesis is implemented and tested
- clean ancillas are restored correctly
- exhaustive clean-subspace verification passes
- Toffoli matrix, statevector, and unitary support are covered
- Toffoli counting is integrated into the resource model
- parallel depth preserves per-qubit dependencies
- documentation is updated
- the full test suite passes
- Week 6 changes are committed

## Week 6 result

Week 6 added a complete reversible-circuit construction and verification layer to the FTQC workbench and integrated it with the existing logical resource model.

**Week 6 status: complete.**
