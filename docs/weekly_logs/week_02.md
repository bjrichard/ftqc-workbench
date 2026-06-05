# Week 2 log — Circuit construction helpers and API polish

## Week 2 objective

Finish the circuit and gate foundation by making the Week 1 circuit Intermediate Representation (IR) easier to use, better tested, and better documented.

By the end of the week, the repo should support simple circuit construction using primitive gate definitions, operation-based construction, and immutable-style helper methods.

## Scope for this week

In scope:

- `Circuit.append_gate()`
- `Circuit.extend()`
- helper-method validation
- public import conventions
- Application Programming Interface (API) examples
- edge-case tests
- weekly stabilization

Out of scope:

- gate matrices
- Clifford+T resource counting
- simulation
- verification
- primitive circuit builders
- optimization passes
- benchmarking
- top-level package re-exports such as `from qc_compiler import Circuit`

## Design decisions

- `append()` remains the lower-level method for appending an `Operation`.
- `append_gate()` is a convenience helper that creates an `Operation` from a `Gate` and concrete qubit indices.
- `append_gate()` delegates validation to `Operation` and `append()`.
- `extend()` appends multiple `Operation` objects while preserving operation order.
- `extend()` accepts only a tuple of `Operation` objects.
- `extend(())` returns a new equivalent `Circuit`.
- Public imports should remain explicit through subpackages.

Expected public imports by the end of the week:

```python
from qc_compiler.gates import X, CNOT
from qc_compiler.circuits import Circuit, Operation
```

## Day 1 — `append_gate()` helper

Goal:

Add a convenience helper for constructing circuits directly from primitive gate definitions.

Files:

- `src/qc_compiler/circuits/circuit.py`
- `tests/circuits/test_circuit.py`

Expected behavior:

- `append_gate()` returns a new circuit.
- The original circuit remains unchanged.
- The added gate is stored as an `Operation`.
- Out-of-range qubit indices fail.
- Non-tuple qubit inputs fail.
- Non-`Gate` inputs fail.

Completion criteria:

- Tests added.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
feat(circuits): add circuit gate append helper
```

## Day 2 — `extend()` helper

Goal:

Add a helper for appending multiple operations while preserving immutable-style behavior.

Files:

- `src/qc_compiler/circuits/circuit.py`
- `tests/circuits/test_circuit.py`

Expected behavior:

- `extend()` returns a new circuit.
- The original circuit remains unchanged.
- Operation order is preserved.
- Non-tuple operation inputs fail.
- Non-`Operation` entries fail.
- Out-of-range operation qubits fail.
- Empty tuples are accepted and return a new equivalent circuit.

Completion criteria:

- Tests added.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
feat(circuits): add circuit extend helper
```

## Day 3 — API examples and public import documentation

Goal:

Document the supported Week 2 public imports and basic circuit construction examples.

Files:

- `src/qc_compiler/__init__.py`
- `docs/api_examples.md`

Expected behavior:

- Package imports work from a clean editable install.
- Public examples use supported imports.
- Documentation avoids unsupported top-level imports.
- Documentation defines Application Programming Interface (API) before using the acronym.

Completion criteria:

- API examples added.
- Public imports checked.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
docs(api): document public circuit and gate imports
```

## Day 4 — Helper edge-case tests

Goal:

Harden circuit helper behavior with missing edge-case tests.

Files:

- `tests/circuits/test_circuit.py`
- `src/qc_compiler/circuits/circuit.py`, only if a test exposes a real implementation gap

Expected behavior:

- `append()` rejects non-`Operation` inputs.
- `append_gate()` rejects wrong qubit counts.
- `append_gate()` rejects non-tuple qubit inputs.
- `append_gate()` rejects non-`Gate` inputs.
- `extend()` accepts an empty tuple.
- `extend()` rejects invalid operation collections.

Completion criteria:

- Edge-case tests added.
- Any implementation gap fixed.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
test(circuits): add circuit helper edge cases
```

## Day 5 — Cleanup, review, and stabilization

Goal:

Stabilize the Week 2 helper layer and prepare for Week 3 resource estimation.

Tasks:

- Run the full test suite.
- Review helper method docstrings.
- Confirm public imports remain clean.
- Confirm `docs/api_examples.md` matches implemented behavior.
- Update this Week 2 log with final notes.
- Confirm no Week 3 work leaked into Week 2.

Completion criteria:

- `pytest` passes.
- Week 2 log updated.
- Known gaps are written down.
- Changes committed.

Suggested commit:

```text
docs(plan): update week 2 completion notes
```

## Final notes

- Added `Circuit.append_gate()` for direct gate-based circuit construction.
- Added `Circuit.extend()` for appending multiple operations.
- Added API examples for gate-based and operation-based construction.
- Added helper edge-case tests.
- Confirmed helper methods preserve immutable-style circuit behavior.
- Resource estimation, simulation, verification, and optimization remain out of scope.

## End-of-week review

1. What was completed?
   - `append_gate()`, `extend()`, API examples, public import checks, and helper edge-case tests.

2. What is behind schedule?
   - Nothing material.

3. What should be cut?
   - Nothing.

4. What should move to backlog?
   - No new items.

5. What is next week’s main deliverable?
   - Resource estimation foundation: `ResourceEstimate`, `ResourceEstimator`, gate counts, T-count, controlled-NOT and controlled-Z counts, simple depth estimate, and ancilla-count convention.

6. Did any result suggest a publishable angle?
   - No. The project remains a portfolio/software-engineering foundation at this stage.

7. Do any scope-cut triggers apply?
   - No.

## Week 2 definition of done

Week 2 is done when:

- `append_gate()` works and is tested.
- `extend()` works and is tested.
- Public circuit and gate imports are documented.
- Helper edge cases are tested.
- `docs/api_examples.md` reflects current supported behavior.
- The package structure remains aligned with `PROJECT_CONTROL.md`.
- `pytest` passes.
- Work is committed with clear commit messages.
