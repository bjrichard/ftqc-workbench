# Readout mitigation notes

## Purpose

This note defines the initial readout-error mitigation feature for the
Fault-Tolerant Quantum Computing (FTQC) workbench.

The goal is to add one small applied quantum engineering component without
turning the project into a full noisy simulator.

The feature should correct measured bitstring probabilities using a known
readout assignment matrix.

## Motivation

Quantum hardware measurements are imperfect. Even if the quantum state before
measurement is correct, the classical bit reported by the device can be wrong.

For a single qubit, readout error can be represented by an assignment matrix:

\[
A =
\begin{pmatrix}
P(0_{\mathrm{meas}}|0_{\mathrm{true}}) &
P(0_{\mathrm{meas}}|1_{\mathrm{true}}) \\
P(1_{\mathrm{meas}}|0_{\mathrm{true}}) &
P(1_{\mathrm{meas}}|1_{\mathrm{true}})
\end{pmatrix}.
\]

If \(p_{\mathrm{true}}\) is the ideal probability vector and
\(p_{\mathrm{meas}}\) is the observed probability vector, then:

\[
p_{\mathrm{meas}} = A p_{\mathrm{true}}.
\]

Readout mitigation estimates:

\[
p_{\mathrm{true}} \approx A^{-1} p_{\mathrm{meas}}.
\]

This is a classical post-processing correction. It does not simulate gate
noise, decoherence, crosstalk, or faulty unitary evolution.

## Initial scope

In scope:

- single-qubit readout-error mitigation
- input measured counts as `dict[str, int]`
- convert counts to probabilities
- validate a 2-by-2 assignment matrix
- invert the assignment matrix
- return mitigated probabilities as `dict[str, float]`
- clip or reject clearly invalid numerical cases according to an explicit
  convention

Out of scope:

- multi-qubit tensor-product correction
- correlated readout errors
- calibration fitting
- shot-noise uncertainty estimates
- covariance propagation
- Bayesian mitigation
- constrained least-squares mitigation
- quasiprobability mitigation
- gate noise
- noisy statevector simulation
- density-matrix simulation
- hardware backend integration

## Proposed package location

Implementation file:

```text
src/qc_compiler/mitigation/readout.py
```

Tests:

```text
tests/mitigation/test_readout.py
```

The mitigation package already exists as a placeholder. This feature should
make it concrete without expanding the rest of the simulator stack.

## Input conventions

### Counts

The first implementation should accept a single-qubit counts dictionary:

```python
{"0": 90, "1": 10}
```

Requirements:

- keys must be strings
- allowed keys are `"0"` and `"1"`
- values must be nonnegative integers
- at least one count must be positive
- missing outcomes are treated as zero

Examples:

```python
{"0": 100}
```

is equivalent to:

```python
{"0": 100, "1": 0}
```

and:

```python
{"1": 100}
```

is equivalent to:

```python
{"0": 0, "1": 100}
```

### Assignment matrix

The assignment matrix should be a NumPy array with shape `(2, 2)`.

Column convention:

```text
assignment_matrix[measured_bit, true_bit]
```

So:

```python
assignment_matrix[0, 1]
```

means:

```text
P(measured 0 | true 1)
```

Each column should sum to one because each true state must be assigned to some
measured outcome.

The matrix must be invertible. Singular assignment matrices cannot be used for
linear inversion mitigation.

## Output convention

The first implementation should return mitigated probabilities, not integer
counts.

Example output:

```python
{"0": 0.95, "1": 0.05}
```

Returning probabilities avoids pretending that mitigation reconstructs actual
integer shot counts.

## Numerical convention

Linear inversion can produce small negative probabilities because of finite
sampling noise or ill-conditioned assignment matrices.

The first implementation should use a simple explicit convention:

1. compute the linear-inversion estimate
2. clip small negative values to zero
3. renormalize the result to sum to one

This is not statistically optimal, but it is simple, inspectable, and suitable
for the current project scope.

The implementation should raise an error if the corrected probability vector
cannot be normalized after clipping.

## Proposed public API

```python
def mitigate_single_qubit_readout(
    counts: dict[str, int],
    assignment_matrix: np.ndarray,
) -> dict[str, float]:
    ...
```

Behavior:

1. validate `counts`
2. validate `assignment_matrix`
3. convert counts to measured probabilities
4. solve or invert the assignment matrix
5. clip negative probabilities to zero
6. renormalize
7. return a probability dictionary with keys `"0"` and `"1"`

## Example

Suppose the observed counts are:

```python
counts = {"0": 90, "1": 10}
```

and the assignment matrix is:

```python
assignment_matrix = np.array(
    [
        [0.95, 0.10],
        [0.05, 0.90],
    ],
    dtype=float,
)
```

Then the model is:

```text
p_measured = assignment_matrix @ p_true
```

The mitigation estimate is:

```text
p_true ≈ inverse(assignment_matrix) @ p_measured
```

The returned result should be a normalized probability dictionary.

## Testing strategy

Tests should cover:

- identity assignment matrix returns observed probabilities
- symmetric readout error is corrected in the expected direction
- missing `"0"` or `"1"` keys are treated as zero
- invalid count keys are rejected
- negative counts are rejected
- non-integer counts are rejected
- empty counts are rejected
- all-zero counts are rejected
- assignment matrix with wrong shape is rejected
- nonnumeric assignment matrix is rejected
- columns that do not sum to one are rejected
- singular assignment matrix is rejected
- output probabilities sum to one
- output keys are exactly `"0"` and `"1"`

The tests should start with deterministic hand-computable examples rather than
randomized cases.

## Relationship to existing project conventions

This feature is classical post-processing. It should not interact with the
statevector simulator, basis-state simulator, circuit builders, or resource
estimator.

It belongs in `qc_compiler.mitigation` because it acts on measured classical
data after circuit execution.

The implementation should keep bitstring conventions explicit. For the
single-qubit case, there is no endian ambiguity. Multi-qubit extension should
not be added until bitstring ordering is specified carefully.

## Future extensions

Possible later extensions include:

- tensor-product multi-qubit readout mitigation
- correlated readout assignment matrices
- constrained least-squares correction
- uncertainty estimates from finite shots
- mitigation examples using simulated noisy counts
- integration with benchmark or experiment result objects

These should remain deferred until the single-qubit implementation is complete,
tested, and documented.
