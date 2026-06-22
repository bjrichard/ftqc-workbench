from __future__ import annotations

import numpy as np
import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import H, X, Z
from qc_compiler.verification import (
    circuits_equivalent_up_to_global_phase,
    unitaries_equivalent_up_to_global_phase,
)


def test_identical_unitaries_are_equivalent() -> None:
    """Treat identical matrices as equivalent."""
    first = np.eye(2, dtype=complex)
    second = np.eye(2, dtype=complex)

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is True


def test_unitaries_differing_by_negative_one_are_equivalent() -> None:
    """Recognize a global phase of negative one."""
    first = np.eye(2, dtype=complex)
    second = -first

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is True


def test_unitaries_differing_by_imaginary_phase_are_equivalent() -> None:
    """Recognize a global phase of imaginary one."""
    first = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=complex,
    )
    second = 1j * first

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is True


def test_unitaries_differing_by_general_phase_are_equivalent() -> None:
    """Recognize an arbitrary unit-magnitude global phase."""
    first = np.array(
        [
            [1, 1],
            [1, -1],
        ],
        dtype=complex,
    ) / np.sqrt(2)
    phase = np.exp(1j * 0.37)
    second = phase * first

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is True


def test_different_unitaries_are_not_equivalent() -> None:
    """Reject matrices not related by one global phase."""
    first = np.eye(2, dtype=complex)
    second = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=complex,
    )

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is False


def test_relative_sign_difference_is_not_global_phase() -> None:
    """Reject a phase difference applied to only part of a matrix."""
    first = np.eye(2, dtype=complex)
    second = np.array(
        [
            [1, 0],
            [0, -1],
        ],
        dtype=complex,
    )

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is False


def test_phase_reference_does_not_require_nonzero_top_left_entry() -> None:
    """Find a valid phase reference when the first entry is zero."""
    first = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=complex,
    )
    second = -first

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is True


def test_nonunit_magnitude_scaling_is_not_global_phase() -> None:
    """Reject multiplication by a nonunit scale factor."""
    first = np.eye(2, dtype=complex)
    second = 2 * first

    result = unitaries_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is False


@pytest.mark.parametrize(
    ("argument_name", "first", "second"),
    [
        (
            "first",
            [[1, 0], [0, 1]],
            np.eye(2, dtype=complex),
        ),
        (
            "second",
            np.eye(2, dtype=complex),
            [[1, 0], [0, 1]],
        ),
    ],
)
def test_rejects_nonarray_input(
    argument_name: str,
    first: object,
    second: object,
) -> None:
    """Reject either argument when it is not a NumPy array."""
    with pytest.raises(
        TypeError,
        match=f"{argument_name} must be a NumPy array",
    ):
        unitaries_equivalent_up_to_global_phase(
            first,  # type: ignore[arg-type]
            second,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("argument_name", "first", "second"),
    [
        (
            "first",
            np.array([1, 0], dtype=complex),
            np.eye(2, dtype=complex),
        ),
        (
            "second",
            np.eye(2, dtype=complex),
            np.array([1, 0], dtype=complex),
        ),
        (
            "first",
            np.zeros((2, 3), dtype=complex),
            np.eye(2, dtype=complex),
        ),
        (
            "second",
            np.eye(2, dtype=complex),
            np.zeros((2, 3), dtype=complex),
        ),
    ],
)
def test_rejects_nonsquare_matrix(
    argument_name: str,
    first: np.ndarray,
    second: np.ndarray,
) -> None:
    """Reject either argument when it is not a square matrix."""
    with pytest.raises(
        ValueError,
        match=f"{argument_name} must be a square matrix",
    ):
        unitaries_equivalent_up_to_global_phase(
            first,
            second,
        )


def test_rejects_empty_matrices() -> None:
    """Reject empty square matrices."""
    first = np.empty((0, 0), dtype=complex)
    second = np.empty((0, 0), dtype=complex)

    with pytest.raises(
        ValueError,
        match="Matrices must be nonempty",
    ):
        unitaries_equivalent_up_to_global_phase(
            first,
            second,
        )


def test_rejects_different_matrix_shapes() -> None:
    """Reject square matrices with different dimensions."""
    first = np.eye(2, dtype=complex)
    second = np.eye(4, dtype=complex)

    with pytest.raises(
        ValueError,
        match="Matrices must have the same shape",
    ):
        unitaries_equivalent_up_to_global_phase(
            first,
            second,
        )


def test_identical_empty_circuits_are_equivalent() -> None:
    """Treat identical empty circuits as equivalent."""
    first = Circuit(
        num_qubits=1,
        operations=(),
    )
    second = Circuit(
        num_qubits=1,
        operations=(),
    )

    result = circuits_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is True


def test_identical_nonempty_circuits_are_equivalent() -> None:
    """Treat identical nonempty circuits as equivalent."""
    first = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=H,
                qubits=(0,),
            ),
        ),
    )
    second = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=H,
                qubits=(0,),
            ),
        ),
    )

    result = circuits_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is True


def test_two_pauli_x_gates_are_equivalent_to_identity() -> None:
    """Recognize that applying Pauli-X twice implements identity."""
    identity_circuit = Circuit(
        num_qubits=1,
        operations=(),
    )
    x_operation = Operation(
        gate=X,
        qubits=(0,),
    )
    double_x_circuit = Circuit(
        num_qubits=1,
        operations=(
            x_operation,
            x_operation,
        ),
    )

    result = circuits_equivalent_up_to_global_phase(
        identity_circuit,
        double_x_circuit,
    )

    assert result is True


def test_circuits_differing_by_global_phase_are_equivalent() -> None:
    """Recognize circuits whose unitaries differ by a global phase."""
    identity_circuit = Circuit(
        num_qubits=1,
        operations=(),
    )
    negative_identity_circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=X,
                qubits=(0,),
            ),
            Operation(
                gate=Z,
                qubits=(0,),
            ),
            Operation(
                gate=X,
                qubits=(0,),
            ),
            Operation(
                gate=Z,
                qubits=(0,),
            ),
        ),
    )

    result = circuits_equivalent_up_to_global_phase(
        identity_circuit,
        negative_identity_circuit,
    )

    assert result is True


def test_different_circuits_are_not_equivalent() -> None:
    """Reject circuits that implement different unitaries."""
    identity_circuit = Circuit(
        num_qubits=1,
        operations=(),
    )
    x_circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=X,
                qubits=(0,),
            ),
        ),
    )

    result = circuits_equivalent_up_to_global_phase(
        identity_circuit,
        x_circuit,
    )

    assert result is False


def test_circuits_with_different_register_sizes_are_not_equivalent() -> None:
    """Reject circuits acting on different register sizes."""
    first = Circuit(
        num_qubits=1,
        operations=(),
    )
    second = Circuit(
        num_qubits=2,
        operations=(),
    )

    result = circuits_equivalent_up_to_global_phase(
        first,
        second,
    )

    assert result is False


def test_circuit_equivalence_rejects_noncircuit_first_argument() -> None:
    """Reject a first argument that is not a Circuit."""
    second = Circuit(
        num_qubits=1,
        operations=(),
    )

    with pytest.raises(
        TypeError,
        match="first must be a Circuit object",
    ):
        circuits_equivalent_up_to_global_phase(
            "not a circuit",  # type: ignore[arg-type]
            second,
        )


def test_circuit_equivalence_rejects_noncircuit_second_argument() -> None:
    """Reject a second argument that is not a Circuit."""
    first = Circuit(
        num_qubits=1,
        operations=(),
    )

    with pytest.raises(
        TypeError,
        match="second must be a Circuit object",
    ):
        circuits_equivalent_up_to_global_phase(
            first,
            "not a circuit",  # type: ignore[arg-type]
        )
