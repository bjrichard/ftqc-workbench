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
    ``p_true``. Entries produced by linear inversion are clipped to zero and the
    result is renormalized. This clipping convention is simple and explicit,
    but it is not a statistically optimal constrained estimator.
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

    mitigated_probabilities = _mitigate_probabilities(
        measured_probabilities=measured_probabilities,
        assignment_matrix=assignment_matrix,
        singular_message="assignment_matrix must be invertible.",
    )

    return {
        "0": float(mitigated_probabilities[0]),
        "1": float(mitigated_probabilities[1]),
    }


def mitigate_tensor_product_readout(
    counts: dict[str, int],
    assignment_matrices: tuple[np.ndarray, ...],
) -> dict[str, float]:
    """Mitigate tensor-product multi-qubit readout error.

    Parameters
    ----------
    counts
        Measured bitstring counts. All provided bitstrings must have length
        equal to the number of assignment matrices. Missing bitstrings are
        treated as zero counts.
    assignment_matrices
        Tuple of single-qubit assignment matrices. The matrix at index ``q``
        describes readout error for qubit ``q`` using the convention
        ``assignment_matrix[measured_bit, true_bit]``.

    Returns
    -------
    dict[str, float]
        Mitigated probability distribution over all computational-basis
        bitstrings in binary order.

    Raises
    ------
    TypeError
        If ``assignment_matrices`` is not a tuple, or if count or assignment
        matrix validation fails.
    ValueError
        If ``assignment_matrices`` is empty, if any count key has the wrong
        length, if the assignment matrices are invalid, if the tensor-product
        assignment matrix is singular, or if the mitigated probabilities cannot
        be normalized.

    Notes
    -----
    Bitstrings use conventional display order: ``"q_{n-1}...q_1q_0"``. The
    rightmost character is qubit 0 and the least-significant bit.

    The full assignment matrix is built as ``A_{n-1} ⊗ ... ⊗ A_1 ⊗ A_0`` so
    that binary-ordered probability vectors align with displayed bitstrings.
    This implements independent per-qubit readout errors only. Correlated
    readout errors are not modeled.
    """
    _validate_assignment_matrices(assignment_matrices)

    num_qubits = len(assignment_matrices)
    _validate_tensor_product_counts(counts, num_qubits=num_qubits)

    bitstrings = _bitstrings(num_qubits)
    total_shots = sum(counts.values())

    measured_probabilities = np.array(
        [
            counts.get(bitstring, 0) / total_shots
            for bitstring in bitstrings
        ],
        dtype=float,
    )

    full_assignment_matrix = _tensor_product_assignment_matrix(
        assignment_matrices,
    )

    mitigated_probabilities = _mitigate_probabilities(
        measured_probabilities=measured_probabilities,
        assignment_matrix=full_assignment_matrix,
        singular_message="tensor-product assignment matrix must be invertible.",
    )

    return {
        bitstring: float(probability)
        for bitstring, probability in zip(
            bitstrings,
            mitigated_probabilities,
            strict=True,
        )
    }


def _mitigate_probabilities(
    *,
    measured_probabilities: np.ndarray,
    assignment_matrix: np.ndarray,
    singular_message: str,
) -> np.ndarray:
    """Solve a readout mitigation linear system and normalize probabilities.

    Parameters
    ----------
    measured_probabilities
        Measured probability vector.
    assignment_matrix
        Assignment matrix mapping true probabilities to measured
        probabilities.
    singular_message
        Error message to use if the assignment matrix is singular.

    Returns
    -------
    np.ndarray
        Clipped and normalized mitigated probability vector.

    Raises
    ------
    ValueError
        If the assignment matrix is singular or if the mitigated probabilities
        cannot be normalized.

    Notes
    -----
    The solved model is ``p_measured = assignment_matrix @ p_true``. The result
    is clipped at zero and renormalized according to the mitigation convention
    used throughout this module.
    """
    try:
        mitigated_probabilities = np.linalg.solve(
            assignment_matrix,
            measured_probabilities,
        )
    except np.linalg.LinAlgError as exc:
        raise ValueError(singular_message) from exc

    mitigated_probabilities = np.clip(
        mitigated_probabilities,
        a_min=0.0,
        a_max=None,
    )

    normalization = float(np.sum(mitigated_probabilities))

    if normalization <= 0.0:
        raise ValueError("Mitigated probabilities cannot be normalized.")

    return mitigated_probabilities / normalization


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
    _validate_counts_like_dictionary(counts)

    allowed_keys = {"0", "1"}

    for bitstring, count in counts.items():
        if bitstring not in allowed_keys:
            raise ValueError('count keys must be "0" or "1".')

        if count < 0:
            raise ValueError("count values must be nonnegative.")

    total_shots = counts.get("0", 0) + counts.get("1", 0)

    if total_shots <= 0:
        raise ValueError("counts must contain at least one shot.")


def _validate_tensor_product_counts(
    counts: dict[str, int],
    *,
    num_qubits: int,
) -> None:
    """Validate multi-qubit measured-count input.

    Parameters
    ----------
    counts
        Candidate multi-qubit counts dictionary.
    num_qubits
        Required bitstring length.

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
        If any count key is empty, has the wrong length, contains characters
        other than ``"0"`` and ``"1"``, if any count is negative, or if the
        total shot count is zero.
    """
    _validate_counts_like_dictionary(counts)

    total_shots = 0

    for bitstring, count in counts.items():
        if bitstring == "":
            raise ValueError("count keys must be nonempty bitstrings.")

        if len(bitstring) != num_qubits:
            raise ValueError(f"count keys must have length {num_qubits}.")

        if any(bit not in {"0", "1"} for bit in bitstring):
            raise ValueError('count keys must contain only "0" and "1".')

        if count < 0:
            raise ValueError("count values must be nonnegative.")

        total_shots += count

    if total_shots <= 0:
        raise ValueError("counts must contain at least one shot.")


def _validate_counts_like_dictionary(counts: dict[str, int]) -> None:
    """Validate shared measured-count dictionary conventions.

    Parameters
    ----------
    counts
        Candidate measured-count dictionary.

    Returns
    -------
    None
        The function returns no value when validation succeeds.

    Raises
    ------
    TypeError
        If ``counts`` is not a dictionary, if any key is not a string, or if
        any count value is not an integer or is a Boolean.
    """
    if not isinstance(counts, dict):
        raise TypeError("counts must be a dictionary.")

    for bitstring, count in counts.items():
        if not isinstance(bitstring, str):
            raise TypeError("count keys must be strings.")

        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count values must be integers.")


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
    Invertibility is checked by the public mitigation functions when solving
    the linear system. Keeping that check at the solve site preserves the
    original numerical exception context.
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

    if not np.allclose(column_sums, np.ones(2)):
        raise ValueError("assignment_matrix columns must sum to one.")


def _validate_assignment_matrices(
    assignment_matrices: tuple[np.ndarray, ...],
) -> None:
    """Validate tensor-product single-qubit assignment matrices.

    Parameters
    ----------
    assignment_matrices
        Candidate tuple of single-qubit assignment matrices.

    Returns
    -------
    None
        The function returns no value when validation succeeds.

    Raises
    ------
    TypeError
        If ``assignment_matrices`` is not a tuple.
    ValueError
        If ``assignment_matrices`` is empty or any assignment matrix is invalid.
    """
    if not isinstance(assignment_matrices, tuple):
        raise TypeError("assignment_matrices must be a tuple.")

    if len(assignment_matrices) == 0:
        raise ValueError("assignment_matrices must be nonempty.")

    for assignment_matrix in assignment_matrices:
        _validate_assignment_matrix(assignment_matrix)


def _bitstrings(num_qubits: int) -> tuple[str, ...]:
    """Return computational-basis bitstrings in binary order.

    Parameters
    ----------
    num_qubits
        Number of qubits represented by each bitstring.

    Returns
    -------
    tuple[str, ...]
        Bitstrings ordered by their usual binary integer value.

    Notes
    -----
    Bitstrings use display order ``"q_{n-1}...q_1q_0"``. The rightmost
    character is qubit 0 and the least-significant bit.
    """
    return tuple(
        format(index, f"0{num_qubits}b")
        for index in range(2**num_qubits)
    )


def _tensor_product_assignment_matrix(
    assignment_matrices: tuple[np.ndarray, ...],
) -> np.ndarray:
    """Build the full tensor-product assignment matrix.

    Parameters
    ----------
    assignment_matrices
        Tuple of single-qubit assignment matrices where index ``q`` gives the
        assignment matrix for qubit ``q``.

    Returns
    -------
    np.ndarray
        Full assignment matrix ordered as ``A_{n-1} ⊗ ... ⊗ A_1 ⊗ A_0``.

    Notes
    -----
    With binary-ordered probability vectors and displayed bitstrings
    ``"q_{n-1}...q_1q_0"``, the rightmost bit is qubit 0. Therefore the
    rightmost tensor factor must be the assignment matrix for qubit 0.
    """
    full_assignment_matrix = assignment_matrices[-1]

    for assignment_matrix in reversed(assignment_matrices[:-1]):
        full_assignment_matrix = np.kron(
            full_assignment_matrix,
            assignment_matrix,
        )

    return full_assignment_matrix
