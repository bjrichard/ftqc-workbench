# Week 8 log — Integer adder planning and initial implementation

## Week 8 objective

Start the integer adder primitive family by selecting a source construction, defining the builder API, pinning down validation behavior, and implementing the first verified small cases.

The goal of Week 8 was not to complete the full general adder. It was to establish the correct source, semantics, register convention, and implementation path before generalizing.

## Scope for this week

In scope:

- select an integer adder construction
- document the intended adder semantics
- define the builder API
- add validation tests
- export the public builder
- implement and verify one-bit modular addition
- implement and verify two-bit modular addition
- explicitly reject unsupported larger registers

Out of scope:

- full general n-bit Cuccaro synthesis
- carry-in or carry-out variants
- subtraction
- controlled addition
- modular reduction
- multiplication
- benchmarking the adder
- Clifford+T decomposition
- T-depth
- routing-aware resource estimation

## Completed work

### Day 1 — Integer adder planning

Created `docs/integer_adder_notes.md`.

Documented the purpose of the integer adder primitive, intended modular in-place behavior, initial verification strategy, benchmark sizes, and open decisions.

### Day 2 — Source and construction selection

Selected the Cuccaro-Draper-Kutin-Moulton ripple-carry adder as the source construction.

Updated `docs/references.md` with the Cuccaro adder reference.

### Day 3 — Builder API decision

Documented the proposed builder API:

```python
build_cuccaro_adder(
    a: tuple[int, ...],
    b: tuple[int, ...],
    carry: int,
    *,
    num_qubits: int,
) -> Circuit
```

The intended operation is:

\[
|a\rangle |b\rangle |0\rangle
\mapsto
|a\rangle |a+b \bmod 2^n\rangle |0\rangle.
\]

### Day 4 — Validation and one-bit behavior

Added validation tests for the Cuccaro adder builder.

Implemented and exported `build_cuccaro_adder`.

Implemented the one-bit modular addition case:

```text
b[0] <- b[0] XOR a[0]
```

This is represented by one Controlled-NOT (CNOT) gate from `a[0]` to `b[0]`.

### Day 5 — Two-bit modular behavior

Added exhaustive two-bit truth-table verification.

Implemented the two-bit modular adder case with:

```text
TOFFOLI(a[0], b[0], b[1])
CNOT(a[1], b[1])
CNOT(a[0], b[0])
```

The test verifies that:

- the `a` register is preserved
- the `b` register becomes `(a + b) mod 2**n`
- the clean carry qubit remains zero

Larger registers currently raise `NotImplementedError`.

## Current implementation status

Implemented:

- `n = 1`
- `n = 2`

Not yet implemented:

- general `n >= 3` Cuccaro majority/unmajority-and-add synthesis

The current implementation is intentionally partial. It avoids claiming support for a general Cuccaro adder until the full majority/unmajority-and-add sequence is derived, implemented, and verified.

## Design decisions

- `a[0]` and `b[0]` are least-significant bits.
- `a` and `b` must be equal-length nonempty tuples.
- Tuple entries are circuit qubit indices.
- Tuple positions are register bit positions.
- The `a` register is preserved.
- The `b` register is overwritten with the modular sum.
- `carry` is a clean work qubit.
- Carry-in and carry-out behavior are not exposed in the first API.
- Larger unsupported register sizes fail explicitly.

## End-of-week review

1. What was completed?
   - Integer adder source selection, API documentation, validation tests, public builder export, one-bit adder behavior, and two-bit exhaustive verification.

2. What is behind schedule?
   - The full general n-bit Cuccaro adder is not implemented yet, but this is acceptable because Week 8 was started early after Week 7 completed ahead of schedule.

3. What should be cut?
   - Nothing from the current adder path.

4. What should move to backlog?
   - Carry-in/carry-out variants, subtraction, controlled addition, modular reduction, multiplication, and arithmetic optimizations remain deferred.

5. What is next week’s main deliverable?
   - Derive and implement the general Cuccaro majority/unmajority-and-add sequence for `n >= 3`, starting with exhaustive verification for `n = 3`.

6. Did any result suggest a publishable angle?
   - No. The current result is useful portfolio-quality primitive implementation work, not a novel research contribution.

7. Do any scope-cut triggers apply?
   - No.
