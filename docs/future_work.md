# Future work roadmap

## Purpose

This roadmap identifies the best next extensions after the initial 12-week
Fault-Tolerant Quantum Computing (FTQC) workbench project.

The goal is not to list every possible feature. The goal is to identify the
highest-value next steps that would deepen the workbench while preserving its
current strengths:

- explicit conventions
- testable abstractions
- deterministic verification
- reproducible benchmarks
- honest resource-model boundaries

Future work should remain narrow, inspectable, and tied to measurable behavior.

## Prioritization principle

The best next features are the ones that improve the workbench as an applied
quantum software and engineering artifact.

A good extension should satisfy most of the following:

- exposes an important quantum software engineering concept
- strengthens the resource-estimation story
- has clear correctness tests
- can be benchmarked deterministically
- does not require premature hardware assumptions
- keeps implemented scope separate from future scope

## Priority 1 — Circuit intermediate representation improvements

### Add explicit qubit-role metadata

Current limitation:

The generic `Circuit` object knows only the number of qubits and the ordered
operations. It does not retain whether a qubit was used as an input register,
target register, clean ancilla, dirty ancilla, carry/work qubit, or output
register.

This is why generic resource estimates currently report:

```text
ancilla_count = 0
```

even when a construction-level benchmark separately records required workspace.

Proposed extension:

Add optional role metadata to circuit builders or a wrapper object, such as:

```text
input_qubits
output_qubits
clean_ancillas
dirty_ancillas
work_qubits
```

Value:

- improves resource reports
- makes workspace assumptions explicit
- clarifies reversible primitive contracts
- supports cleaner benchmark tables

Risk:

Avoid overcomplicating the core `Circuit` class too early. A separate metadata
object may be better than modifying the circuit intermediate representation
directly.

Recommended next step:

Prototype role metadata for the multi-controlled Pauli-X and Cuccaro adder
builders only.

## Priority 2 — Circuit composition

Current limitation:

The workbench does not yet support composing circuits that act on the same
register or embedding one circuit into another.

Proposed extension:

Add explicit circuit composition with validation.

Useful cases:

- concatenate circuits over the same qubit register
- embed a smaller circuit into selected qubits of a larger circuit
- preserve immutability
- reject invalid remappings
- keep operation order explicit

Value:

- enables larger examples without hand-writing operation lists
- supports future compiler passes
- makes the workbench feel more like a real quantum software stack

Key design question:

Whether composition should be a method on `Circuit`, a free function, or a
separate transformation utility.

Recommended next step:

Start with same-register composition only:

```python
compose_circuits(first: Circuit, second: Circuit) -> Circuit
```

Do not start with arbitrary qubit remapping. That can come later.

## Priority 3 — Actual Toffoli decomposition

Current limitation:

The workbench supports analytical Toffoli-expanded T-count estimates using:

```text
1 Toffoli = 7 T gates
```

but it does not actually decompose Toffoli gates into Clifford+T circuits.

Proposed extension:

Implement one named Toffoli decomposition and expose it as a circuit
transformation.

Value:

- connects primitive logical resources to explicit gate-level circuits
- enables actual post-decomposition gate counts
- creates a path toward T-depth estimation
- strengthens the fault-tolerant resource story

Required discipline:

The decomposition must cite a source and define its exact convention. The
project should not vaguely say “decompose Toffoli” without specifying which
decomposition is implemented.

Recommended next step:

Add a transformation such as:

```python
decompose_toffoli_to_clifford_t(circuit: Circuit) -> Circuit
```

only after documenting the selected decomposition and verifying it by exact
unitary simulation.

## Priority 4 — T-depth estimation

Current limitation:

The workbench estimates serial depth and dependency-preserving parallel depth,
but it does not estimate T-depth.

T-depth depends on an explicit decomposition and scheduling convention.

Proposed extension:

After actual Toffoli decomposition exists, add a T-depth estimator.

Value:

- moves resource estimates beyond scalar T-count
- introduces a core fault-tolerant quantum computing metric
- makes benchmark tables more informative

Do not implement this before decomposition.

Recommended dependency:

```text
Toffoli decomposition first, T-depth second.
```

## Priority 5 — Correlated readout-error mitigation

Current limitation:

The mitigation module supports independent per-qubit readout errors through
tensor-product assignment matrices.

It does not support correlated assignment matrices.

Proposed extension:

Support a full `2**n` by `2**n` assignment matrix as public input.

Value:

- represents correlated measurement errors
- generalizes the current mitigation model
- keeps the feature in classical post-processing scope

Risk:

Full assignment matrices scale exponentially, so this should be documented as
a small-system feature.

Recommended next step:

Add a separate function rather than overloading the tensor-product helper:

```python
mitigate_correlated_readout(
    counts: dict[str, int],
    assignment_matrix: np.ndarray,
) -> dict[str, float]
```

## Priority 6 — Constrained readout mitigation

Current limitation:

The current readout mitigation convention uses linear inversion, clips
negative entries to zero, and renormalizes.

This is simple and inspectable, but not statistically optimal.

Proposed extension:

Add constrained least-squares mitigation.

Value:

- avoids ad hoc clipping as the primary estimator
- keeps output probabilities nonnegative and normalized
- introduces a more realistic mitigation method

Risk:

This likely requires an additional dependency or a careful small custom solver.
Do not add it unless dependency policy is clear.

Recommended next step:

Document the mathematical formulation first:

```text
minimize ||A p_true - p_measured||_2
subject to p_true >= 0
and sum(p_true) = 1
```

Then decide whether to implement.

## Priority 7 — Compiler-pass infrastructure

Current limitation:

The repository has early compiler-pass scaffolding, but the project does not
yet demonstrate a meaningful transformation pass.

Proposed extension:

Add one simple, deterministic circuit rewrite pass.

Candidate passes:

- remove adjacent self-inverse gate pairs
- cancel adjacent duplicate Controlled-NOT (CNOT) gates on the same qubits
- cancel adjacent duplicate Pauli-X gates on the same qubit
- decompose Toffoli gates after the decomposition is implemented

Value:

- demonstrates compiler thinking
- creates before-and-after resource estimates
- connects the workbench to quantum software engineering roles

Recommended next step:

Start with a conservative cancellation pass whose correctness is easy to test.

## Priority 8 — Benchmark comparison artifacts

Current limitation:

Benchmarks currently report resource tables for implemented primitives, but
they do not yet show before-and-after effects of transformations.

Proposed extension:

Add comparison benchmarks after transformation passes exist.

Examples:

- primitive circuit vs decomposed Clifford+T circuit
- unoptimized circuit vs cancellation-pass output
- logical primitive count vs expanded/decomposed count

Value:

- makes resource-model changes concrete
- gives reviewers easy evidence of engineering discipline
- supports portfolio storytelling

Do not add comparison tables without a real transformation to compare.

## Recommended next three extensions

If this project continues after Week 12, the strongest sequence is:

1. Same-register circuit composition
2. Explicit Toffoli decomposition with tests
3. T-depth estimation for decomposed circuits

This sequence is better than jumping directly to hardware estimates because it
keeps assumptions controlled and builds naturally from the current workbench.

## Lower-priority extensions

These may be useful later, but they should not be first:

- hardware coupling-map routing
- surface-code distance estimates
- physical qubit estimates
- magic-state factory models
- integration with a production quantum software development kit (SDK)
- large algorithm implementations
- density-matrix simulation
- stochastic noisy simulation

These are valid directions, but each introduces substantial assumptions. They
should wait until the logical and decomposition layers are stronger.

## What not to do next

Do not immediately turn the workbench into a broad quantum software development
kit clone.

Avoid adding:

- many gates without use cases
- many algorithms without resource analysis
- hardware estimates without error-model assumptions
- noisy simulation without clear validation targets
- compiler abstractions without at least one real pass
- documentation that implies unimplemented capabilities

The project is strongest when it stays explicit, small, testable, and honest.

## Summary

The best future direction is to deepen the resource-estimation path:

```text
logical primitive circuits
→ explicit composition
→ explicit decomposition
→ T-depth and richer logical resources
→ transformation comparisons
→ carefully scoped hardware-facing estimates
```

Readout mitigation can also deepen in parallel, but it should remain clearly
separated from circuit construction, ideal simulation, and logical resource
estimation.
