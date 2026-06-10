# Week 5 log — Exact simulation and equivalence foundation

## Week 5 objective

Build the first exact simulation layer for small circuits and establish the conventions needed for later equivalence checking.

By the end of the week, the repo should support primitive gate matrices, statevector simulation for small circuits, circuit-to-unitary construction, and equivalence checking up to global phase.

This week is governed by the project control plan section for Weeks 4–5: exact simulation and equivalence.

## Scope for this week

In scope:

- primitive gate matrices
- NumPy-based complex matrix representation
- little-endian statevector indexing
- documentation of basis ordering conventions
- applying single operations to statevectors
- simulating small circuits on statevectors
- constructing small circuit unitaries
- checking unitary equivalence up to global phase
- tests on known identities and hand-derived examples

Out of scope:

- reversible truth-table simulation
- multi-controlled Toffoli construction
- integer adder construction
- local optimization passes
- Clifford tableau simulation
- hardware-aware simulation
- noise simulation
- measurement and feedforward
- large-scale simulation
- decision diagram methods

## Design decisions

- Simulation uses NumPy arrays with complex dtype.
- Primitive gate matrices are retrieved through `get_gate_matrix`.
- Gate matrices are returned as copies so callers cannot mutate the internal matrix table.
- Statevector indexing uses little-endian qubit indexing.
- Qubit `0` is the least significant bit.
- Basis indices are computed as `q0 * 2^0 + q1 * 2^1 + ... + q_{n-1} * 2^{n-1}`.
- For two qubits, basis vectors are ordered by integer index as `|00>`, `|01>`, `|10>`, `|11>`.
- Under the little-endian convention, the displayed bit string is interpreted as `|q1 q0>`, not `|q0 q1>`.
- Therefore `|01>` means `q1 = 0` and `q0 = 1`.
- The detailed source of truth for simulation basis conventions is `docs/simulation_conventions.md`.
- Controlled-NOT (CNOT) on qubits `(0, 1)` means qubit `0` is the control and qubit `1` is the target.
- Global phase is ignored for unitary equivalence checks.

## Daily plan

### Day 1 — Primitive gate matrices and simulation conventions

Add primitive gate matrices for the initial exact simulator.

Expected deliverables:

- `src/qc_compiler/simulation/matrices.py`
- `src/qc_compiler/simulation/__init__.py`
- `tests/simulation/test_matrices.py`
- `docs/simulation_conventions.md`

Primitive gates initially supported:

- identity (`I`)
- Pauli-X (`X`)
- Pauli-Y (`Y`)
- Pauli-Z (`Z`)
- Hadamard (`H`)
- phase gate (`S`)
- T gate (`T`)
- controlled-NOT (`CNOT`)
- controlled-Z (`CZ`)

Expected commit:

```bash
feat(simulation): add primitive gate matrices
```

### Day 2 — Apply operations to statevectors

Add functionality for applying a single circuit operation to a statevector under the documented little-endian convention.

Expected deliverables:

- operation application helper
- tests for one-qubit operations
- tests for two-qubit operations
- tests that verify little-endian controlled-NOT behavior

Expected commit:

```bash
feat(simulation): apply operations to statevectors
```

### Day 3 — Simulate full circuits on statevectors

Add full circuit statevector simulation by applying operations in circuit order.

Expected deliverables:

- statevector simulator function or minimal simulator object
- tests for empty circuits
- tests for simple one-qubit circuits
- tests for simple two-qubit circuits
- tests on known identities where practical

Expected commit:

```bash
feat(simulation): add statevector circuit simulation
```

### Day 4 — Circuit unitaries and equivalence up to global phase

Add small circuit-to-unitary construction and equivalence checking up to global phase.

Expected deliverables:

- circuit-to-unitary conversion for small circuits
- equivalence checker up to global phase
- tests for equivalent circuits
- tests for non-equivalent circuits
- tests for global-phase equivalence

Expected commit:

```bash
feat(verification): add unitary equivalence checker
```

### Day 5 — Documentation, cleanup, and completion log

Review Week 5 simulation and equivalence code, documentation, tests, and public imports.

Expected deliverables:

- update this Week 5 log into a completion log
- update documentation if conventions or limitations changed
- run full test suite
- verify public imports

Expected commit:

```bash
docs(plan): add week 5 completion log
```

## Completion criteria

Week 5 is complete when:

- primitive gate matrices are implemented and tested
- simulation basis conventions are documented
- statevector simulation works for small circuits
- circuit-to-unitary construction works for small circuits
- equivalence checking up to global phase works for small circuits
- known identities are tested
- all simulation assumptions are explicit
- the full test suite passes
- Week 5 changes are committed and pushed

## Drift warning

Do not start multi-controlled Toffoli construction, integer adders, local optimization, or T-depth work during Week 5 unless exact simulation and equivalence are already complete.

Those items remain important, but they depend on the verification backbone that Week 5 is intended to build.
