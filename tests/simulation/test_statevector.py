"""Tests for statevector operation application and circuit simulation."""

from __future__ import annotations

import numpy as np
import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, H, X, Z
from qc_compiler.simulation import (
    apply_operation_to_statevector,
    simulate_statevector,
)
from qc_compiler.simulation.statevector import (
    _extract_local_index,
    _get_bit,
    _infer_num_qubits,
    _replace_local_bits,
    _set_bit,
)


@pytest.mark.parametrize(
    ("size", "expected_num_qubits"),
    [
        (1, 0),
        (2, 1),
        (4, 2),
        (8, 3),
        (16, 4),
    ],
)
def test_infer_num_qubits_from_valid_statevector_size(
    size: int,
    expected_num_qubits: int,
) -> None:
    """Infer qubit count from a power-of-two statevector length."""
    statevector = np.zeros(size, dtype=complex)

    result = _infer_num_qubits(statevector)

    assert result == expected_num_qubits


def test_infer_num_qubits_rejects_nonvector_array() -> None:
    """Reject a statevector that is not one-dimensional."""
    statevector = np.zeros((2, 2), dtype=complex)

    with pytest.raises(
        ValueError,
        match="Statevector must be one-dimensional",
    ):
        _infer_num_qubits(statevector)


def test_infer_num_qubits_rejects_empty_statevector() -> None:
    """Reject an empty statevector."""
    statevector = np.array([], dtype=complex)

    with pytest.raises(
        ValueError,
        match="Statevector must be nonempty",
    ):
        _infer_num_qubits(statevector)


def test_infer_num_qubits_rejects_non_power_of_two_length() -> None:
    """Reject a statevector whose length is not a power of two."""
    statevector = np.zeros(6, dtype=complex)

    with pytest.raises(
        ValueError,
        match="Statevector length must be a power of two",
    ):
        _infer_num_qubits(statevector)


@pytest.mark.parametrize(
    ("index", "position", "expected_bit"),
    [
        (0b1010, 0, 0),
        (0b1010, 1, 1),
        (0b1010, 2, 0),
        (0b1010, 3, 1),
    ],
)
def test_get_bit_returns_requested_bit(
    index: int,
    position: int,
    expected_bit: int,
) -> None:
    """Return the bit stored at the requested integer position."""
    result = _get_bit(index, position)

    assert result == expected_bit


def test_set_bit_sets_zero_bit_to_one() -> None:
    """Set a selected zero bit to one."""
    index = 0b1001

    result = _set_bit(index=index, position=2, bit=1)

    assert result == 0b1101


def test_set_bit_clears_one_bit_to_zero() -> None:
    """Clear a selected one bit to zero."""
    index = 0b1101

    result = _set_bit(index=index, position=2, bit=0)

    assert result == 0b1001


def test_set_bit_preserves_existing_one_bit() -> None:
    """Preserve a selected bit that is already one."""
    index = 0b1010

    result = _set_bit(index=index, position=1, bit=1)

    assert result == index


def test_set_bit_preserves_existing_zero_bit() -> None:
    """Preserve a selected bit that is already zero."""
    index = 0b1010

    result = _set_bit(index=index, position=0, bit=0)

    assert result == index


@pytest.mark.parametrize("bit", [-1, 2, 3])
def test_set_bit_rejects_nonbinary_value(bit: int) -> None:
    """Reject a replacement value other than zero or one."""
    with pytest.raises(
        ValueError,
        match="bit must be zero or one",
    ):
        _set_bit(index=0, position=0, bit=bit)


def test_extract_local_index_packs_selected_bits() -> None:
    """Pack selected full-register bits into local positions."""
    result = _extract_local_index(
        basis_index=0b1010,
        qubits=(1, 2, 3),
    )

    assert result == 0b101


def test_extract_local_index_respects_qubit_tuple_order() -> None:
    """Treat tuple order as the definition of local bit positions."""
    basis_index = 0b1000

    forward = _extract_local_index(
        basis_index=basis_index,
        qubits=(3, 0),
    )
    reversed_order = _extract_local_index(
        basis_index=basis_index,
        qubits=(0, 3),
    )

    assert forward == 0b01
    assert reversed_order == 0b10


def test_replace_local_bits_replaces_selected_positions() -> None:
    """Replace selected bits while preserving untouched bits."""
    result = _replace_local_bits(
        basis_index=0b0101,
        qubits=(0, 1),
        local_index=0b10,
    )

    assert result == 0b0110


def test_replace_local_bits_supports_nonadjacent_qubits() -> None:
    """Replace nonadjacent selected bits."""
    result = _replace_local_bits(
        basis_index=0b0011,
        qubits=(0, 3),
        local_index=0b10,
    )

    assert result == 0b1010


def test_apply_pauli_x_to_qubit_zero() -> None:
    """Apply Pauli-X to the least significant qubit."""
    operation = Operation(gate=X, qubits=(0,))
    statevector = np.array([1, 0, 0, 0], dtype=complex)
    expected = np.array([0, 1, 0, 0], dtype=complex)

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_apply_pauli_x_to_qubit_one() -> None:
    """Apply Pauli-X to the second qubit."""
    operation = Operation(gate=X, qubits=(1,))
    statevector = np.array([1, 0, 0, 0], dtype=complex)
    expected = np.array([0, 0, 1, 0], dtype=complex)

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_apply_hadamard_creates_superposition() -> None:
    """Apply Hadamard and produce two output basis amplitudes."""
    operation = Operation(gate=H, qubits=(0,))
    statevector = np.array([1, 0], dtype=complex)
    expected = np.array([1, 1], dtype=complex) / np.sqrt(2)

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_apply_cnot_uses_first_operation_qubit_as_control() -> None:
    """Apply CNOT using little-endian local indexing."""
    operation = Operation(gate=CNOT, qubits=(0, 1))
    statevector = np.array([0, 1, 0, 0], dtype=complex)
    expected = np.array([0, 0, 0, 1], dtype=complex)

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_apply_cnot_to_nonadjacent_qubits() -> None:
    """Apply CNOT to nonadjacent full-register qubits."""
    operation = Operation(gate=CNOT, qubits=(0, 3))
    statevector = np.zeros(16, dtype=complex)
    statevector[1] = 1

    expected = np.zeros(16, dtype=complex)
    expected[9] = 1

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_apply_pauli_x_moves_superposition_amplitudes() -> None:
    """Move each populated amplitude to the correct output index."""
    operation = Operation(gate=X, qubits=(0,))
    statevector = np.array([1, 2, 0, 0], dtype=complex) / np.sqrt(5)
    expected = np.array([2, 1, 0, 0], dtype=complex) / np.sqrt(5)

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_apply_hadamard_accumulates_superposition_amplitudes() -> None:
    """Accumulate amplitudes from multiple populated input states."""
    operation = Operation(gate=H, qubits=(0,))
    statevector = np.array([1, 1], dtype=complex) / np.sqrt(2)
    expected = np.array([1, 0], dtype=complex)

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_apply_operation_does_not_mutate_input_statevector() -> None:
    """Return a new statevector without modifying the input."""
    operation = Operation(gate=X, qubits=(0,))
    statevector = np.array([1, 0], dtype=complex)
    original = statevector.copy()

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    np.testing.assert_array_equal(statevector, original)
    assert result is not statevector


def test_apply_operation_returns_complex_statevector() -> None:
    """Return a complex statevector even when the input is real."""
    operation = Operation(gate=X, qubits=(0,))
    statevector = np.array([1, 0])

    result = apply_operation_to_statevector(
        operation=operation,
        statevector=statevector,
    )

    assert np.issubdtype(result.dtype, np.complexfloating)


def test_apply_operation_rejects_nonoperation_input() -> None:
    """Reject an operation argument with the wrong type."""
    statevector = np.array([1, 0], dtype=complex)

    with pytest.raises(
        TypeError,
        match="operation must be an Operation",
    ):
        apply_operation_to_statevector(
            operation="X",  # type: ignore[arg-type]
            statevector=statevector,
        )


def test_apply_operation_rejects_nonarray_statevector() -> None:
    """Reject a statevector argument that is not a NumPy array."""
    operation = Operation(gate=X, qubits=(0,))

    with pytest.raises(
        TypeError,
        match="statevector must be a NumPy array",
    ):
        apply_operation_to_statevector(
            operation=operation,
            statevector=[1, 0],  # type: ignore[arg-type]
        )


def test_apply_operation_rejects_out_of_range_qubit() -> None:
    """Reject an operation targeting a qubit outside the register."""
    operation = Operation(gate=X, qubits=(2,))
    statevector = np.array([1, 0, 0, 0], dtype=complex)

    with pytest.raises(
        ValueError,
        match="Operation targets a qubit outside the statevector",
    ):
        apply_operation_to_statevector(
            operation=operation,
            statevector=statevector,
        )


def test_simulate_statevector_returns_zero_state_for_empty_circuit() -> None:
    """Return the all-zero state for an empty circuit."""
    circuit = Circuit(num_qubits=2, operations=())
    expected = np.array([1, 0, 0, 0], dtype=complex)

    result = simulate_statevector(circuit=circuit)

    np.testing.assert_array_equal(result, expected)


def test_simulate_statevector_applies_operations_in_order() -> None:
    """Apply circuit operations in their stored order."""
    circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(gate=H, qubits=(0,)),
            Operation(gate=Z, qubits=(0,)),
        ),
    )
    expected = np.array([1, -1], dtype=complex) / np.sqrt(2)

    result = simulate_statevector(circuit=circuit)

    np.testing.assert_allclose(result, expected)


def test_simulate_statevector_applies_two_pauli_x_gates_as_identity() -> None:
    """Return to the initial state after applying Pauli-X twice."""
    x_operation = Operation(gate=X, qubits=(0,))
    circuit = Circuit(
        num_qubits=1,
        operations=(x_operation, x_operation),
    )
    expected = np.array([1, 0], dtype=complex)

    result = simulate_statevector(circuit=circuit)

    np.testing.assert_allclose(result, expected)


def test_simulate_statevector_prepares_bell_state() -> None:
    """Prepare a Bell state from the all-zero state."""
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(gate=H, qubits=(0,)),
            Operation(gate=CNOT, qubits=(0, 1)),
        ),
    )
    expected = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

    result = simulate_statevector(circuit=circuit)

    np.testing.assert_allclose(result, expected)


def test_simulate_statevector_uses_supplied_initial_statevector() -> None:
    """Simulate a circuit from a supplied initial statevector."""
    circuit = Circuit(
        num_qubits=1,
        operations=(Operation(gate=X, qubits=(0,)),),
    )
    initial_statevector = np.array([0, 1], dtype=complex)
    expected = np.array([1, 0], dtype=complex)

    result = simulate_statevector(
        circuit=circuit,
        initial_statevector=initial_statevector,
    )

    np.testing.assert_allclose(result, expected)


def test_simulate_statevector_does_not_mutate_initial_statevector() -> None:
    """Return a new result without mutating the supplied initial state."""
    circuit = Circuit(
        num_qubits=1,
        operations=(Operation(gate=X, qubits=(0,)),),
    )
    initial_statevector = np.array([0, 1], dtype=complex)
    original = initial_statevector.copy()

    result = simulate_statevector(
        circuit=circuit,
        initial_statevector=initial_statevector,
    )

    np.testing.assert_array_equal(initial_statevector, original)
    assert result is not initial_statevector


def test_simulate_statevector_copies_initial_state_for_empty_circuit() -> None:
    """Return a copy of the supplied state for an empty circuit."""
    circuit = Circuit(num_qubits=1, operations=())
    initial_statevector = np.array([0, 1], dtype=complex)

    result = simulate_statevector(
        circuit=circuit,
        initial_statevector=initial_statevector,
    )

    np.testing.assert_array_equal(result, initial_statevector)
    assert result is not initial_statevector


def test_simulate_statevector_returns_complex_statevector() -> None:
    """Return a complex statevector for a real initial statevector."""
    circuit = Circuit(num_qubits=1, operations=())
    initial_statevector = np.array([1, 0])

    result = simulate_statevector(
        circuit=circuit,
        initial_statevector=initial_statevector,
    )

    assert np.issubdtype(result.dtype, np.complexfloating)


def test_simulate_statevector_rejects_noncircuit_input() -> None:
    """Reject an input that is not a Circuit."""
    with pytest.raises(
        TypeError,
        match="circuit must be a Circuit object",
    ):
        simulate_statevector(
            circuit="not a circuit",  # type: ignore[arg-type]
        )


def test_simulate_statevector_rejects_nonarray_initial_statevector() -> None:
    """Reject an initial statevector that is not a NumPy array."""
    circuit = Circuit(num_qubits=1, operations=())

    with pytest.raises(
        TypeError,
        match="initial_statevector must be a NumPy array",
    ):
        simulate_statevector(
            circuit=circuit,
            initial_statevector=[1, 0],  # type: ignore[arg-type]
        )


def test_simulate_statevector_rejects_nonvector_initial_state() -> None:
    """Reject an initial statevector that is not one-dimensional."""
    circuit = Circuit(num_qubits=2, operations=())
    initial_statevector = np.zeros((2, 2), dtype=complex)

    with pytest.raises(
        ValueError,
        match="Initial statevector must be one-dimensional",
    ):
        simulate_statevector(
            circuit=circuit,
            initial_statevector=initial_statevector,
        )


def test_simulate_statevector_rejects_incorrect_initial_state_size() -> None:
    """Reject an initial statevector with the wrong register size."""
    circuit = Circuit(num_qubits=2, operations=())
    initial_statevector = np.array([1, 0], dtype=complex)

    with pytest.raises(
        ValueError,
        match=(
            "Initial statevector size must match the circuit "
            "register size"
        ),
    ):
        simulate_statevector(
            circuit=circuit,
            initial_statevector=initial_statevector,
        )
