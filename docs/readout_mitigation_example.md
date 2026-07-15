# Readout mitigation example

## Purpose

This example shows how to use the single-qubit readout-error mitigation helper.

The feature performs classical post-processing on measured counts. It corrects
observed bitstring probabilities using a known readout assignment matrix.

It does not simulate noisy quantum evolution, gate error, decoherence,
crosstalk, or hardware execution.

## Model

For one qubit, the assignment matrix is:

\[
A =
\begin{pmatrix}
P(0_{\mathrm{meas}}|0_{\mathrm{true}}) &
P(0_{\mathrm{meas}}|1_{\mathrm{true}}) \\
P(1_{\mathrm{meas}}|0_{\mathrm{true}}) &
P(1_{\mathrm{meas}}|1_{\mathrm{true}})
\end{pmatrix}.
\]

The convention is:

```text
assignment_matrix[measured_bit, true_bit]
```

The model is:

\[
p_{\mathrm{meas}} = A p_{\mathrm{true}}.
\]

The mitigation estimate solves:

\[
p_{\mathrm{true}} \approx A^{-1}p_{\mathrm{meas}}.
\]

## Example

```python
import numpy as np

from qc_compiler.mitigation import mitigate_single_qubit_readout


counts = {"0": 820, "1": 180}

assignment_matrix = np.array(
    [
        [0.9, 0.1],
        [0.1, 0.9],
    ],
    dtype=float,
)

mitigated = mitigate_single_qubit_readout(
    counts=counts,
    assignment_matrix=assignment_matrix,
)

print(mitigated)
```

Expected output:

```python
{"0": 0.9, "1": 0.1}
```

The measured probability vector is:

\[
p_{\mathrm{meas}} =
\begin{pmatrix}
0.82 \\
0.18
\end{pmatrix}.
\]

The assignment matrix says that each true state is misread as the other state
with probability \(0.1\). Linear inversion estimates the pre-readout-error
probability vector:

\[
p_{\mathrm{true}} =
\begin{pmatrix}
0.9 \\
0.1
\end{pmatrix}.
\]

## Missing outcomes

Missing outcomes are treated as zero counts.

For example:

```python
counts = {"0": 100}
```

is interpreted as:

```python
counts = {"0": 100, "1": 0}
```

The returned result always has both keys:

```python
{"0": ..., "1": ...}
```

## Numerical convention

Linear inversion can produce negative entries because of finite-shot noise or
ill-conditioned assignment matrices.

The current implementation uses a simple explicit convention:

1. solve the linear system
2. clip negative entries to zero
3. renormalize the probability vector

This is not a statistically optimal mitigation method. It is a transparent
first implementation suitable for testing and documentation.

## Limitations

The current implementation supports only:

- one measured qubit
- counts with keys `"0"` and `"1"`
- a known 2-by-2 assignment matrix
- linear inversion mitigation
- probability output

It does not support:

- multi-qubit mitigation
- correlated readout error
- tensor-product assignment matrices
- calibration fitting
- uncertainty estimates
- constrained least-squares mitigation
- Bayesian mitigation
- noisy simulation
- hardware backend integration

## Relationship to the rest of the workbench

This feature is independent of the circuit builders, simulators, and resource
estimators.

It acts only on classical measurement counts after a circuit has already been
executed or simulated elsewhere.
