from __future__ import annotations

import numpy as np

from qc_compiler.circuits import Circuit
from qc_compiler.simulation import circuit_to_unitary


def unitaries_equivalent_up_to_global_phase(
    first: np.ndarray,
    second: np.ndarray,
    *,
    atol: float = 1e-8,
    rtol: float = 1e-5,
) -> bool:
    """
    Check whether two matrices differ only by a global phase.

    Parameters
    ----------
    first : np.ndarray
        First square matrix.
    second : np.ndarray
        Second square matrix.
    atol : float, optional
        Absolute tolerance used for numerical comparison.
    rtol : float, optional
        Relative tolerance used for numerical comparison.

    Returns
    -------
    bool
        ``True`` if the matrices differ only by a unit-magnitude complex
        scalar; otherwise ``False``.

    Raises
    ------
    TypeError
        If either input is not a NumPy array.
    ValueError
        If either input is not a nonempty square matrix or if the matrix
        shapes differ.

    Notes
    -----
    The phase reference is taken from the largest-magnitude entry of
    ``first`` so that a zero-valued reference element is not selected.
    """
    if not isinstance(first, np.ndarray):
        raise TypeError("first must be a NumPy array.")

    if not isinstance(second, np.ndarray):
        raise TypeError("second must be a NumPy array.")

    if first.ndim != 2 or first.shape[0] != first.shape[1]:
        raise ValueError("first must be a square matrix.")

    if second.ndim != 2 or second.shape[0] != second.shape[1]:
        raise ValueError("second must be a square matrix.")

    if first.size == 0 or second.size == 0:
        raise ValueError("Matrices must be nonempty.")

    if first.shape != second.shape:
        raise ValueError("Matrices must have the same shape.")

    reference_index = np.unravel_index(
        np.argmax(np.abs(first)),
        first.shape,
    )
    reference_value = first[reference_index]

    if np.isclose(
        reference_value,
        0.0,
        atol=atol,
        rtol=rtol,
    ):
        return bool(
            np.allclose(
                first,
                second,
                atol=atol,
                rtol=rtol,
            )
        )

    phase = second[reference_index] / reference_value

    if not np.isclose(
        np.abs(phase),
        1.0,
        atol=atol,
        rtol=rtol,
    ):
        return False

    return bool(
        np.allclose(
            second,
            phase * first,
            atol=atol,
            rtol=rtol,
        )
    )


def circuits_equivalent_up_to_global_phase(
    first: Circuit,
    second: Circuit,
    *,
    atol: float = 1e-8,
    rtol: float = 1e-5,
) -> bool:
    """
    Check whether two circuits implement the same unitary up to global phase.

    Parameters
    ----------
    first : Circuit
        First circuit.
    second : Circuit
        Second circuit.
    atol : float, optional
        Absolute tolerance used for numerical comparison.
    rtol : float, optional
        Relative tolerance used for numerical comparison.

    Returns
    -------
    bool
        ``True`` if the circuits implement equivalent unitaries up to
        global phase; otherwise ``False``.

    Raises
    ------
    TypeError
        If either input is not a ``Circuit``.

    Notes
    -----
    Circuits with different register sizes are not equivalent.
    """
    if not isinstance(first, Circuit):
        raise TypeError("first must be a Circuit object.")

    if not isinstance(second, Circuit):
        raise TypeError("second must be a Circuit object.")

    if first.num_qubits != second.num_qubits:
        return False

    first_unitary = circuit_to_unitary(first)
    second_unitary = circuit_to_unitary(second)

    return unitaries_equivalent_up_to_global_phase(
        first_unitary,
        second_unitary,
        atol=atol,
        rtol=rtol,
    )
