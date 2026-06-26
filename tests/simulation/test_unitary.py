from __future__ import annotations

import numpy as np
import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, H, TOFFOLI, X
from qc_compiler.simulation import circuit_to_unitary


def test_circuit_to_unitary_returns_identity_for_empty_one_qubit_circuit() -> None:
    """Return the two-dimensional identity for an empty one-qubit circuit."""
    circuit = Circuit(
        num_qubits=1,
        operations=(),
    )
    expected = np.eye(2, dtype=complex)

    result = circuit_to_unitary(circuit)

    np.testing.assert_array_equal(result, expected)


def test_circuit_to_unitary_returns_identity_for_empty_two_qubit_circuit() -> None:
    """Return the four-dimensional identity for an empty two-qubit circuit."""
    circuit = Circuit(
        num_qubits=2,
        operations=(),
    )
    expected = np.eye(4, dtype=complex)

    result = circuit_to_unitary(circuit)

    np.testing.assert_array_equal(result, expected)


def test_circuit_to_unitary_returns_pauli_x_matrix() -> None:
    """Construct the Pauli-X matrix from a one-gate circuit."""
    circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=X,
                qubits=(0,),
            ),
        ),
    )
    expected = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=complex,
    )

    result = circuit_to_unitary(circuit)

    np.testing.assert_array_equal(result, expected)


def test_circuit_to_unitary_returns_hadamard_matrix() -> None:
    """Construct the Hadamard matrix from a one-gate circuit."""
    circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=H,
                qubits=(0,),
            ),
        ),
    )
    expected = np.array(
        [
            [1, 1],
            [1, -1],
        ],
        dtype=complex,
    ) / np.sqrt(2)

    result = circuit_to_unitary(circuit)

    np.testing.assert_allclose(result, expected)


def test_circuit_to_unitary_returns_identity_for_two_pauli_x_gates() -> None:
    """Return the identity when Pauli-X is applied twice."""
    x_operation = Operation(
        gate=X,
        qubits=(0,),
    )
    circuit = Circuit(
        num_qubits=1,
        operations=(
            x_operation,
            x_operation,
        ),
    )
    expected = np.eye(2, dtype=complex)

    result = circuit_to_unitary(circuit)

    np.testing.assert_array_equal(result, expected)


def test_circuit_to_unitary_returns_cnot_matrix() -> None:
    """Construct the CNOT matrix using qubit zero as the control."""
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(
                gate=CNOT,
                qubits=(0, 1),
            ),
        ),
    )
    expected = np.array(
        [
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
        ],
        dtype=complex,
    )

    result = circuit_to_unitary(circuit)

    np.testing.assert_array_equal(result, expected)


def test_circuit_to_unitary_returns_toffoli_matrix() -> None:
    """Construct the Toffoli matrix using two controls and one target."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 2),
            ),
        ),
    )
    expected = np.eye(8, dtype=complex)
    expected[[3, 7]] = expected[[7, 3]]

    result = circuit_to_unitary(circuit)

    np.testing.assert_array_equal(result, expected)


def test_circuit_to_unitary_rejects_noncircuit_input() -> None:
    """Reject an input that is not a Circuit."""
    with pytest.raises(
        TypeError,
        match="circuit must be a Circuit object",
    ):
        circuit_to_unitary(
            circuit="not a circuit",  # type: ignore[arg-type]
        )
