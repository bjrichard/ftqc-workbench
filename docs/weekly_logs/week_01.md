# Week 1 log — Circuit and gate foundation

## Week 1 objective

Build the first layer of the Fault-Tolerant Quantum Computing (FTQC) workbench: a minimal, well-tested circuit Intermediate Representation (IR) with explicit gate, operation, and circuit abstractions.

By the end of the week, the repo should support construction and inspection of simple circuits using immutable or immutable-like objects.

## Scope for this week

In scope:

- `Gate`
- `Operation`
- `Circuit`
- qubit indexing conventions
- basic validation
- append behavior
- clean public imports
- unit tests

Out of scope:

- gate matrices
- Clifford+T resource counting
- simulation
- verification
- primitive circuit builders
- optimization passes
- benchmarking

## Design decisions

- Qubits are represented by zero-based integer indices.
- `Gate` represents a reusable logical gate definition.
- `Operation` represents a gate applied to specific qubit indices.
- `Circuit` represents an ordered sequence of operations on a fixed number of qubits.
- Circuit append behavior should return a new circuit rather than mutating the existing circuit.
- Validation should fail early with clear errors.
- Public imports should remain simple and stable.

Expected public imports by the end of the week:

```python
from qc_compiler.gates import X, CNOT
from qc_compiler.circuits import Circuit, Operation
```

## Day 1 — Repo skeleton, imports, and `Gate`

Goal:

Confirm the package structure and implement the minimal `Gate` abstraction.

Files:

- `src/qc_compiler/gates/gate.py`
- `src/qc_compiler/gates/__init__.py`
- `tests/gates/test_gate.py`

Expected behavior:

- Valid gates can be constructed.
- Gate names must be non-empty strings.
- Gate arity must be a positive integer.
- Gate objects are inspectable.
- `Gate` can be imported from `qc_compiler.gates`.

Completion criteria:

- Tests added.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
feat(gates): add basic gate abstraction
```

## Day 2 — `Operation`

Goal:

Implement `Operation` as a gate applied to concrete qubit indices.

Files:

- `src/qc_compiler/circuits/operation.py`
- `src/qc_compiler/circuits/__init__.py`
- `tests/circuits/test_operation.py`

Expected behavior:

- Valid operations can be constructed.
- Operation qubit count must match gate arity.
- Duplicate qubit indices fail.
- Negative qubit indices fail.
- Operation objects are inspectable.
- `Operation` can be imported from `qc_compiler.circuits`.

Completion criteria:

- Tests added.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
feat(circuits): add operation abstraction
```

## Day 3 — `Circuit`

Goal:

Implement `Circuit` as an ordered sequence of operations on a fixed number of qubits.

Files:

- `src/qc_compiler/circuits/circuit.py`
- `src/qc_compiler/circuits/__init__.py`
- `tests/circuits/test_circuit.py`

Expected behavior:

- Valid circuits can be constructed.
- Invalid circuit sizes fail.
- Appending an operation returns a new circuit.
- The original circuit remains unchanged after append.
- Operations using out-of-range qubits fail.
- Circuits support basic inspection, such as length and iteration.
- `Circuit` can be imported from `qc_compiler.circuits`.

Completion criteria:

- Tests added.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
feat(circuits): add immutable circuit container
```

## Day 4 — Primitive logical gates and documentation

Goal:

Add a small logical gate library and document the initial IR conventions.

Likely gates:

- `I`
- `X`
- `Y`
- `Z`
- `H`
- `S`
- `T`
- `CNOT`
- `CZ`
- `TOFFOLI`

Files:

- `src/qc_compiler/gates/library.py`
- `src/qc_compiler/gates/__init__.py`
- `tests/gates/test_library.py`
- `docs/resource_model.md`

Expected behavior:

- Gates have correct names and arities.
- Gates are importable from `qc_compiler.gates`.
- Gate definitions remain simple and inspectable.
- `docs/resource_model.md` documents current assumptions and limitations.

Resource-model documentation should include:

- zero-based qubit indexing
- gate/operation/circuit responsibilities
- current logical gate set
- statement that matrices, simulation, measurements, feedforward, routing, and surface-code costs are not yet modeled
- statement that resource counting begins in Week 3, not Week 1

Completion criteria:

- Gate constants added.
- Tests added for names, arities, and imports.
- Documentation updated.
- `pytest` passes.
- Changes committed.

Suggested commit:

```text
feat(gates): add primitive logical gate library
```

Optional documentation commit if the docs update is substantial:

```text
docs(circuits): document initial IR conventions
```

## Day 5 — Cleanup, review, and stabilization

Goal:

Stabilize the Week 1 foundation and avoid carrying design debt forward.

Tasks:

- Review names and module boundaries.
- Confirm imports are clean.
- Confirm tests are organized correctly.
- Remove accidental complexity.
- Add missing edge-case tests.
- Check docstrings and error messages.
- Run the full test suite.
- Update this Week 1 log with final notes.

Completion criteria:

- `pytest` passes.
- Week 1 log updated.
- Known gaps are written down.
- Changes committed.

Suggested commit:

```text
test(circuits): stabilize basic circuit IR tests
```

## Final notes

- Implemented `Gate`, `Operation`, and `Circuit`.
- Added primitive logical gate definitions.
- Documented initial circuit Intermediate Representation (IR) and resource-model assumptions.
- Confirmed public imports for `qc_compiler.gates` and `qc_compiler.circuits`.
- Resource counting, matrices, simulation, verification, and optimization remain out of scope.

## End-of-week review notes

1. What was completed?
   - `Gate`, `Operation`, `Circuit`, primitive logical gates, public imports, tests, and initial resource-model documentation.

2. What is behind schedule?
   - Nothing material.

3. What should be cut?
   - Nothing.

4. What should move to backlog?
   - No new items.

5. What is next week’s main deliverable?
   - Circuit construction helpers and additional gate/circuit polish, while keeping simulation and resource estimation out of scope.

6. Did any result suggest a publishable angle?
   - No. The project remains a portfolio/software-engineering foundation at this stage.

7. Do any scope-cut triggers apply?
   - No.

## Week 1 definition of done

Week 1 is done when:

- `Gate`, `Operation`, and `Circuit` exist.
- Basic validation is tested.
- Primitive logical gates are defined and importable.
- Simple circuits can be constructed and inspected.
- `docs/resource_model.md` has initial Week 1 assumptions.
- The package structure remains aligned with `PROJECT_CONTROL.md`.
- `pytest` passes.
- Work is committed with clear commit messages.
