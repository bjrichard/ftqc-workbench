# Week 11 log — Readout-error mitigation

## Objective

Add one small applied quantum engineering component to the workbench: classical
readout-error mitigation.

The goal was not to build a full noisy simulator. The goal was to add a focused,
testable post-processing feature that connects the circuit workbench to a real
near-term hardware concern.

## Summary

Week 11 added single-qubit and tensor-product multi-qubit readout mitigation.

The implementation takes measured bitstring counts, applies a known assignment
matrix model, solves a linear inversion problem, clips negative probabilities,
renormalizes the result, and returns mitigated probabilities.

This feature is classical post-processing. It does not modify circuits or
simulate noisy quantum evolution.

## Day 1 — Design note

Added:

```text
docs/readout_mitigation_notes.md
```

The design note defined:

- the single-qubit assignment-matrix model
- the convention `assignment_matrix[measured_bit, true_bit]`
- the linear model `p_measured = A @ p_true`
- the initial public API
- the decision to return probabilities rather than corrected counts
- validation expectations
- numerical convention for negative values
- scope boundaries and future extensions

Key decision:

```text
Readout mitigation should live in qc_compiler.mitigation because it acts on
classical measurement data after execution.
```

## Day 2 — Single-qubit implementation

Added:

```text
src/qc_compiler/mitigation/readout.py
tests/mitigation/test_readout.py
```

Updated:

```text
src/qc_compiler/mitigation/__init__.py
```

Implemented:

```python
mitigate_single_qubit_readout(
    counts: dict[str, int],
    assignment_matrix: np.ndarray,
) -> dict[str, float]
```

The function supports:

- single-qubit counts with keys `"0"` and `"1"`
- missing outcomes treated as zero
- 2-by-2 assignment matrices
- column-stochastic assignment-matrix validation
- linear inversion using `np.linalg.solve`
- clipping negative entries to zero
- renormalization
- probability output

Tests cover:

- identity assignment matrix behavior
- hand-computable symmetric error correction
- missing outcomes
- invalid count input
- invalid assignment matrices
- singular assignment matrices
- normalized output

## Day 3 — Example documentation

Added:

```text
docs/readout_mitigation_example.md
```

The example explains:

- the single-qubit assignment-matrix model
- the bit/column convention
- a hand-computable example
- missing outcome behavior
- clipping and renormalization
- limitations of the implementation

This made the feature usable from the documentation without requiring a reader
to inspect the tests first.

## Day 4 — Tensor-product multi-qubit extension

Extended:

```python
mitigate_tensor_product_readout(
    counts: dict[str, int],
    assignment_matrices: tuple[np.ndarray, ...],
) -> dict[str, float]
```

The function supports independent per-qubit readout errors.

For `n` qubits, bitstrings use conventional display order:

```text
"q_{n-1}...q_1q_0"
```

The rightmost bit is qubit 0 and the least-significant bit.

The full assignment matrix is built as:

```text
A_full = A_{n-1} ⊗ ... ⊗ A_1 ⊗ A_0
```

This aligns the tensor-product assignment matrix with binary-ordered bitstrings:

```text
"00", "01", "10", "11", ...
```

Tests cover:

- identity tensor-product mitigation
- agreement with the single-qubit helper for one qubit
- a hand-computable two-qubit independent-error example
- returning all bitstrings
- rejecting empty assignment-matrix tuples
- rejecting non-tuple assignment-matrix collections
- rejecting wrong bitstring lengths

A regression was caught during this refactor: the single-qubit public function
briefly returned a NumPy array instead of `dict[str, float]`. The tests caught
the public API regression, and the implementation was corrected before commit.

## Current public API

```python
from qc_compiler.mitigation import (
    mitigate_single_qubit_readout,
    mitigate_tensor_product_readout,
)
```

Single-qubit mitigation:

```python
mitigate_single_qubit_readout(
    counts={"0": 820, "1": 180},
    assignment_matrix=assignment_matrix,
)
```

Tensor-product multi-qubit mitigation:

```python
mitigate_tensor_product_readout(
    counts={"00": 8100, "01": 900, "10": 900, "11": 100},
    assignment_matrices=(assignment_matrix_q0, assignment_matrix_q1),
)
```

## Implemented scope

The readout-mitigation module now supports:

- measured counts as `dict[str, int]`
- single-qubit readout mitigation
- independent multi-qubit tensor-product readout mitigation
- explicit bitstring ordering
- explicit assignment-matrix convention
- linear inversion
- clipping negative entries
- renormalization
- probability output
- validation and tests

## Non-goals

The implementation does not support:

- correlated readout-error models
- full `2**n` by `2**n` correlated assignment matrices as public input
- calibration fitting
- finite-shot uncertainty estimates
- covariance propagation
- Bayesian mitigation
- constrained least-squares mitigation
- quasiprobability mitigation
- gate-noise simulation
- density-matrix simulation
- hardware backend integration

## Design notes

The implementation deliberately uses `np.linalg.solve` rather than explicitly
forming a matrix inverse.

This is numerically better practice for solving:

```text
A @ p_true = p_measured
```

The clipping-and-renormalization rule is simple and inspectable, but it is not
a statistically optimal estimator. It is acceptable for this workbench stage
because the goal is to implement and test the core assignment-matrix correction
model, not to build a full mitigation research library.

## Validation status

Run before closeout:

```bash
pytest -q
ruff check .
```

Expected status:

```text
all tests pass
ruff passes
```

## Portfolio relevance

This week adds a practical quantum engineering feature rather than another
idealized circuit primitive.

It demonstrates:

- awareness of measurement error as a hardware-facing issue
- clean separation between circuit construction, simulation, resource
  estimation, and mitigation
- explicit conventions for bitstrings and assignment matrices
- test-first development
- regression detection during refactoring
- narrow scope control
- documentation of limitations

## Status

Week 11 is complete.

The workbench now has:

- ideal circuit construction
- exact simulation
- basis-state verification
- primitive and expanded resource estimates
- benchmark artifacts
- readout-error mitigation
