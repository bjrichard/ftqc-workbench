# Week 12 log — Final project polish

## Objective

Complete the final consolidation week for the Fault-Tolerant Quantum Computing
(FTQC) workbench.

The goal for Week 12 was not to add another major feature. The goal was to make
the project reviewer-ready by clarifying the final scope, updating the main
documentation, and recording future work without implying unimplemented
capabilities.

## Summary

Week 12 focused on portfolio polish and final project consolidation.

The workbench already had the core technical pieces in place:

- immutable circuit intermediate representation
- primitive gate definitions
- exact simulation and basis-state verification
- clean-ancilla multi-controlled Pauli-X construction
- Cuccaro-style modular addition
- primitive and Toffoli-expanded resource estimates
- deterministic benchmark artifacts
- readout-error mitigation

The final week updated the surrounding documentation so that the repository is
easier to inspect, run, evaluate, and extend.

## Day 1 — Final project audit

Added:

```text
docs/final_project_audit.md
```

The audit recorded the final state of the project across five areas:

- what is implemented
- what is tested
- what is documented
- what is benchmarked
- what remains future work

The purpose of the audit was to guide final-week polish rather than serve as a
weekly progress log.

Key conclusion:

```text
The strongest final-week move is consolidation, not feature expansion.
```

## Day 2 — README update

Updated:

```text
README.md
```

The README was revised to reflect the final project state.

Key updates included:

- adding readout-error mitigation to the project overview
- adding `src/qc_compiler/mitigation/` to the module tree and repository guide
- documenting the readout-mitigation public API at a high level
- clarifying benchmark locations
- keeping physical hardware estimates, routing, scheduling, T-depth, and
  magic-state factories explicitly out of scope
- aligning the status section with the implemented project

The README now serves as the front door for a reviewer.

## Day 3 — Technical details update

Updated:

```text
docs/technical_details.md
```

The technical details document was revised to align with the final README and
Week 11 implementation work.

Key updates included:

- documenting the final bitstring convention
- clarifying integer-register indexing conventions
- documenting single-qubit readout mitigation
- documenting tensor-product multi-qubit readout mitigation
- recording the tensor-product assignment-matrix order
- separating implemented readout mitigation from future correlated mitigation
- tightening limitations and future-work language

Important convention:

```text
Displayed bitstrings use "q_{n-1}...q_1q_0"; the rightmost bit is qubit 0.
```

For tensor-product readout mitigation, assignment matrices are ordered as:

```text
A_full = A_{n-1} ⊗ ... ⊗ A_1 ⊗ A_0
```

## Day 4 — Future-work roadmap

Added:

```text
docs/future_work.md
```

The roadmap identified the best next extensions after the initial 12-week
project.

The highest-priority future directions are:

1. same-register circuit composition
2. explicit Toffoli decomposition into Clifford+T gates
3. T-depth estimation after decomposition exists
4. richer resource-estimation comparisons
5. correlated and constrained readout mitigation

The roadmap deliberately avoids presenting a broad wishlist. It prioritizes
extensions that strengthen the workbench as an applied quantum software and
resource-estimation artifact.

## Day 5 — Final validation and summary

Day 5 closes the 12-week project.

Validation commands:

```bash
pytest -q
ruff check .
mypy src
```

Expected status:

```text
all tests pass
ruff passes
mypy passes
```

If `mypy src` is not part of the regular validation workflow yet, it should be
run and any current status should be recorded separately rather than hidden.

## Final implemented scope

At the end of the 12-week project, the workbench includes:

### Circuit model

- immutable `Circuit` objects
- reusable `Gate` definitions
- `Operation` objects applied to concrete qubit indices
- validation of qubit indices and gate arity

### Gate library

- identity gate
- Pauli gates
- Hadamard gate
- phase gates
- Controlled-NOT (CNOT)
- Controlled-Z (CZ)
- Toffoli gate

### Simulation and verification

- exact statevector simulation
- basis-state reversible simulation
- unitary construction
- equivalence checks up to global phase
- exhaustive verification for small reversible primitives
- deterministic randomized verification for larger primitives

### Reversible primitive builders

- clean-ancilla multi-controlled Pauli-X
- Cuccaro-style modular ripple-carry adder

### Resource estimation

- primitive logical gate counts
- CNOT count
- CZ count
- Toffoli count
- primitive T-count
- logical qubit count
- serial depth
- dependency-preserving parallel depth
- analytical Toffoli-expanded T-count estimate

### Benchmarks

- reproducible multi-controlled Pauli-X benchmark
- reproducible Cuccaro adder benchmark
- benchmark documentation and saved comma-separated values (CSV) outputs

### Readout-error mitigation

- single-qubit readout mitigation
- tensor-product multi-qubit readout mitigation
- explicit assignment-matrix convention
- explicit bitstring convention
- linear inversion using `np.linalg.solve`
- clipping and renormalization convention
- validation and tests

## Final limitations

The workbench remains intentionally limited.

It does not implement:

- production compiler infrastructure
- general circuit composition
- arbitrary qubit remapping
- hardware routing
- topology-aware scheduling
- gate-duration scheduling
- explicit Clifford+T Toffoli decomposition
- T-depth estimation
- physical qubit estimates
- surface-code distance estimates
- magic-state factory estimates
- stochastic noisy simulation
- density-matrix simulation
- correlated readout-error mitigation
- hardware backend integration

These omissions are appropriate. The project is a logical-circuit,
verification, resource-accounting, benchmark, and readout-post-processing
workbench—not a production compiler or physical resource estimator.

## Portfolio assessment

The strongest signals in the finished project are:

- explicit technical conventions
- narrow, inspectable abstractions
- test-first implementation style
- deterministic resource benchmarks
- separation of primitive logical counts from expanded analytical estimates
- separation of ideal simulation from classical readout mitigation
- honest documentation of assumptions and limitations

The project is small, but it is coherent. That is the right outcome for an
initial portfolio artifact.

## Suggested final tag

After the final Week 12 log is committed and validation passes, tag the
completed initial project state:

```bash
git tag -a v0.1.0 -m "Complete initial FTQC workbench project"
git push origin v0.1.0
```

This gives the repository a stable reference point for the completed 12-week
version.

## Status

Week 12 is complete.

The initial 12-week FTQC workbench project is complete.
