from __future__ import annotations

import numpy as np


def mitigate_single_qubit_readout(
    counts: dict[str, int],
    assignment_matrix: np.ndarray,
) -> dict[str, float]:
    """Mitigate single-qubit readout error using linear inversion.

    Parameters
    ----------
    counts
        Measured single-qubit bitstring counts. Allowed keys are ``"0"`` and
        ``"1"``. Missing outcomes are treated as zero. Count values must be
        nonnegative integers, and at least one total shot must be present.
    assignment_matrix
        Two-by-two readout assignment matrix with convention
        ``assignment_matrix[measured_bit, true_bit]``. Each column represents
        the conditional measured-outcome distribution for one true basis state
        and must sum to one.

    Returns
    -------
    dict[str, float]
        Mitigated probability distribution with keys ``"0"`` and ``"1"``.
        The probabilities are clipped at zero after linear inversion and then
        renormalized.

    Raises
    ------
    TypeError
        If ``counts`` is not a dictionary, if any count key is not a string, if
        any count value is not an integer or is a Boolean, or if
        ``assignment_matrix`` is not a NumPy array.
    ValueError
        If counts contain unsupported bitstrings, if any count is negative, if
        total shots are zero, if the assignment matrix has the wrong shape, if
        it contains non-finite values, if its columns do not sum to one, if it
        is singular, or if the mitigated probabilities cannot be normalized.

    Notes
    -----
    This function performs classical post-processing only. It does not simulate
    gate noise, measurement noise, state collapse, decoherence, crosstalk, or
    hardware execution.

    The implemented model is

    ``p_measured = assignment_matrix @ p_true``.

    The mitigation estimate is obtained by solving this linear system for
    ``p_true``. Small or large negative entries produced by linear inversion
    are clipped to zero and the result is renormalized. This clipping convention
    is simple and explicit, but it is not a statistically optimal constrained
    estimator.
    """
    _validate_counts(counts)
    _validate_assignment_matrix(assignment_matrix)

    total_shots = counts.get("0", 0) + counts.get("1", 0)

    measured_probabilities = np.array(
        [
            counts.get("0", 0) / total_shots,
            counts.get("1", 0) / total_shots,
        ],
        dtype=float,
    )

    try:
        mitigated_probabilities = np.linalg.solve(
            assignment_matrix,
            measured_probabilities,
        )
    except np.linalg.LinAlgError as exc:
        raise ValueError("assignment_matrix must be invertible.") from exc

    mitigated_probabilities = np.clip(
        mitigated_probabilities,
        a_min=0.0,
        a_max=None,
    )

    normalization = float(np.sum(mitigated_probabilities))

    if normalization <= 0.0:
        raise ValueError("Mitigated probabilities cannot be normalized.")

    mitigated_probabilities = mitigated_probabilities / normalization

    return {
        "0": float(mitigated_probabilities[0]),
        "1": float(mitigated_probabilities[1]),
    }


def _validate_counts(counts: dict[str, int]) -> None:
    """Validate single-qubit measured-count input.

    Parameters
    ----------
    counts
        Candidate single-qubit counts dictionary.

    Returns
    -------
    None
        The function returns no value when validation succeeds.

    Raises
    ------
    TypeError
        If ``counts`` is not a dictionary, if any key is not a string, or if
        any count value is not an integer or is a Boolean.
    ValueError
        If an unsupported bitstring key is present, if any count is negative,
        or if the total shot count is zero.

    Notes
    -----
    Missing ``"0"`` or ``"1"`` outcomes are allowed and treated as zero by the
    public mitigation function.
    """
    if not isinstance(counts, dict):
        raise TypeError("counts must be a dictionary.")

    allowed_keys = {"0", "1"}

    for bitstring, count in counts.items():
        if not isinstance(bitstring, str):
            raise TypeError("count keys must be strings.")

        if bitstring not in allowed_keys:
            raise ValueError('count keys must be "0" or "1".')

        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count values must be integers.")

        if count < 0:
            raise ValueError("count values must be nonnegative.")

    total_shots = counts.get("0", 0) + counts.get("1", 0)

    if total_shots <= 0:
        raise ValueError("counts must contain at least one shot.")


def _validate_assignment_matrix(assignment_matrix: np.ndarray) -> None:
    """Validate a single-qubit readout assignment matrix.

    Parameters
    ----------
    assignment_matrix
        Candidate assignment matrix with convention
        ``assignment_matrix[measured_bit, true_bit]``.

    Returns
    -------
    None
        The function returns no value when validation succeeds.

    Raises
    ------
    TypeError
        If ``assignment_matrix`` is not a NumPy array.
    ValueError
        If the matrix shape is not ``(2, 2)``, if the matrix cannot be
        interpreted numerically, if it contains non-finite values, if any entry
        is negative, or if its columns do not sum to one.

    Notes
    -----
    Invertibility is checked by the public mitigation function when solving the
    linear system. Keeping that check at the solve site preserves the original
    numerical exception context.
    """
    if not isinstance(assignment_matrix, np.ndarray):
        raise TypeError("assignment_matrix must be a NumPy array.")

    if assignment_matrix.shape != (2, 2):
        raise ValueError("assignment_matrix must have shape (2, 2).")

    if not np.issubdtype(assignment_matrix.dtype, np.number):
        raise ValueError("assignment_matrix must be numeric.")

    if not np.all(np.isfinite(assignment_matrix)):
        raise ValueError("assignment_matrix must contain finite values.")

    if np.any(assignment_matrix < 0):
        raise ValueError("assignment_matrix entries must be nonnegative.")

    column_sums = np.sum(assignment_matrix, axis=0)

    if not np.allclose(column_sums, 1.0):
        raise ValueError("assignment_matrix columns must sum to one.")
