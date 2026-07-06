# Week 7 log — Multi-controlled Pauli-X benchmarking and large-size verification

## Week 7 objective

Turn the existing clean-ancilla multi-controlled Pauli-X implementation into a documented, reproducible, benchmarked primitive family.

The construction itself was completed during Week 6. Week 7 therefore does not reimplement the primitive. Instead, it focuses on benchmark infrastructure, source documentation, reproducible resource tables, and size-dependent verification.

## Scope for this week

In scope:

- source documentation for the multi-controlled Pauli-X construction
- benchmark script for roadmap control sizes
- saved benchmark results
- benchmark documentation
- deterministic randomized verification for larger control counts
- clear distinction between construction-level clean-ancilla requirements and estimator-level `ancilla_count`

Out of scope:

- new multi-controlled Pauli-X synthesis methods
- dirty-ancilla constructions
- relative-phase Toffoli constructions
- Toffoli decomposition into Clifford+T
- T-depth
- routing or topology-aware costs
- physical fault-tolerant resource estimation
- circuit composition

## Completed work

### Day 1 — Benchmark infrastructure and documentation

Added a root-level benchmark script:

```text
benchmarks/benchmark_multi_controlled_x.py
```

The benchmark covers the roadmap control counts:

```text
k = 2, 3, 4, 5, 8, 16
```

For each control count, the script records:

- number of controls
- required clean ancillas
- logical qubit count
- total gate count
- T-gate count
- Controlled-NOT (CNOT) count
- Toffoli count
- serial depth
- dependency-preserving parallel depth

Saved reproducible results to:

```text
docs/benchmarks/multi_controlled_x.csv
```

Added benchmark documentation to:

```text
docs/benchmarks/multi_controlled_x.md
```

Added the first source note to:

```text
docs/references.md
```

The source note classifies the implementation as an educational adaptation of a standard clean-ancilla generalized Toffoli construction rather than a direct line-by-line reproduction of a specific circuit listing.

### Day 2 — Large-size randomized verification

Extended multi-controlled Pauli-X verification with deterministic randomized clean-ancilla tests for:

```text
k = 8, 16
```

The tests verify that:

- inputs are sampled from the clean-ancilla subspace
- the target flips exactly when all controls are one
- the target does not flip otherwise
- clean ancillas are restored correctly as part of exact basis-state simulation

Exact unitary verification is intentionally avoided for these sizes because the generated circuits act on 15 and 31 qubits.

## Benchmark results

For \(k \geq 2\), the benchmark confirms:

\[
N_{\mathrm{ancilla}} = k - 2
\]

\[
N_{\mathrm{qubits}} = 2k - 1
\]

\[
N_{\mathrm{Toffoli}} = 2k - 3
\]

\[
D_{\mathrm{serial}} = D_{\mathrm{parallel}} = 2k - 3
\]

The equal serial and parallel depths reflect the dependency structure of the implemented ladder. Successive Toffoli operations share controls or ancillas, so the current dependency-preserving scheduler exposes no parallelism.

## Design decisions

- Benchmarks live in a root-level `benchmarks/` directory rather than inside `src/qc_compiler/`.
- Benchmark tests live under `tests/benchmarks/`.
- The benchmark records required clean ancillas separately from `ResourceEstimate.ancilla_count`.
- `ResourceEstimate.ancilla_count` remains zero because the circuit Intermediate Representation (IR) does not retain qubit-role metadata.
- Randomized verification uses deterministic pseudo-random sampling so test behavior is reproducible.

## Current status

Week 7 has completed the core benchmark and verification deliverables for the multi-controlled Pauli-X primitive family.

Remaining useful Week 7 work:

- review docs for consistency
- ensure benchmark reproduction commands are clear
- run full tests and linting
- perform end-of-week scope review

## End-of-week review

1. What was completed?
   - Multi-controlled Pauli-X benchmark infrastructure, saved benchmark results, benchmark documentation, source documentation, and deterministic randomized large-size verification.

2. What is behind schedule?
   - Nothing material.

3. What should be cut?
   - Nothing from the current Week 7 scope.

4. What should move to backlog?
   - Dirty-ancilla constructions, relative-phase Toffoli variants, Toffoli decomposition into Clifford+T, T-depth, routing-aware estimates, and circuit composition remain deferred.

5. What is next week’s main deliverable?
   - Begin the integer adder primitive path, starting with source selection and a minimal reversible adder specification.

6. Did any result suggest a publishable angle?
   - No. The result is a solid benchmarked primitive-family implementation, but not yet a novel research contribution.

7. Do any scope-cut triggers apply?
   - No.
