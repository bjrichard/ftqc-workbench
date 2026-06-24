from __future__ import annotations

import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, H, I, TOFFOLI, X
from qc_compiler.simulation import (
    basis_state_permutation,
    simulate_basis_state,
)


def test_identity_leaves_basis_index_unchanged() -> None:
    """Leave a basis index unchanged when applying identity."""
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(
                gate=I,
                qubits=(0,),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b10,
    )

    assert result == 0b10


def test_x_flips_target_bit_from_zero_to_one() -> None:
    """Flip a zero-valued target bit to one."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=X,
                qubits=(1,),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b101,
    )

    assert result == 0b111


def test_x_flips_target_bit_from_one_to_zero() -> None:
    """Flip a one-valued target bit to zero."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=X,
                qubits=(1,),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b111,
    )

    assert result == 0b101


def test_cnot_flips_target_when_control_is_one() -> None:
    """Flip the CNOT target when the control bit is one."""
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(
                gate=CNOT,
                qubits=(0, 1),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b01,
    )

    assert result == 0b11


def test_cnot_leaves_target_unchanged_when_control_is_zero() -> None:
    """Leave the CNOT target unchanged when the control bit is zero."""
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(
                gate=CNOT,
                qubits=(0, 1),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b10,
    )

    assert result == 0b10


def test_nonadjacent_cnot_uses_qubit_indices() -> None:
    """Apply CNOT to nonadjacent qubits using their register indices."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=CNOT,
                qubits=(0, 2),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b001,
    )

    assert result == 0b101


def test_toffoli_flips_target_when_both_controls_are_one() -> None:
    """Flip the Toffoli target when both control bits are one."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 2),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b011,
    )

    assert result == 0b111


def test_toffoli_flips_target_from_one_to_zero() -> None:
    """Clear the Toffoli target when both controls and target are one."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 2),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b111,
    )

    assert result == 0b011


@pytest.mark.parametrize(
    ("basis_index", "expected"),
    (
        (0b000, 0b000),
        (0b001, 0b001),
        (0b010, 0b010),
        (0b100, 0b100),
        (0b101, 0b101),
        (0b110, 0b110),
    ),
)
def test_toffoli_leaves_target_unchanged_unless_both_controls_are_one(
    basis_index: int,
    expected: int,
) -> None:
    """Leave the target unchanged unless both Toffoli controls are one."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 2),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=basis_index,
    )

    assert result == expected


def test_toffoli_respects_nonadjacent_nonordered_qubit_roles() -> None:
    """Respect Toffoli control and target roles for reordered qubits."""
    circuit = Circuit(
        num_qubits=4,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(3, 0, 2),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b1001,
    )

    assert result == 0b1101


def test_operations_are_applied_in_order() -> None:
    """Apply basis-state operations in circuit order."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=X,
                qubits=(0,),
            ),
            Operation(
                gate=X,
                qubits=(1,),
            ),
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 2),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b000,
    )

    assert result == 0b111


@pytest.mark.parametrize(
    "basis_index",
    (-1, 4),
)
def test_invalid_basis_index_raises_value_error(
    basis_index: int,
) -> None:
    """Reject a basis index outside the circuit register."""
    circuit = Circuit(
        num_qubits=2,
        operations=(),
    )

    with pytest.raises(
        ValueError,
        match="basis_index must satisfy",
    ):
        simulate_basis_state(
            circuit=circuit,
            basis_index=basis_index,
        )


@pytest.mark.parametrize(
    "basis_index",
    (1.0, "1", True),
)
def test_non_integer_basis_index_raises_type_error(
    basis_index: object,
) -> None:
    """Reject a basis index that is not an integer."""
    circuit = Circuit(
        num_qubits=2,
        operations=(),
    )

    with pytest.raises(
        TypeError,
        match="basis_index must be an integer",
    ):
        simulate_basis_state(
            circuit=circuit,
            basis_index=basis_index,  # type: ignore[arg-type]
        )


def test_non_circuit_input_raises_type_error() -> None:
    """Reject a circuit argument with the wrong type."""
    with pytest.raises(
        TypeError,
        match="circuit must be a Circuit object",
    ):
        simulate_basis_state(
            circuit="not a circuit",  # type: ignore[arg-type]
            basis_index=0,
        )


def test_unsupported_gate_raises_value_error() -> None:
    """Reject a gate unsupported by basis-state simulation."""
    circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=H,
                qubits=(0,),
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="does not support gate 'H'",
    ):
        simulate_basis_state(
            circuit=circuit,
            basis_index=0,
        )


def test_basis_state_permutation_returns_identity_for_empty_one_qubit_circuit(
) -> None:
    """Return the identity permutation for an empty one-qubit circuit."""
    circuit = Circuit(
        num_qubits=1,
        operations=(),
    )

    result = basis_state_permutation(circuit)

    assert result == (0, 1)


def test_basis_state_permutation_returns_identity_for_empty_two_qubit_circuit(
) -> None:
    """Return the identity permutation for an empty two-qubit circuit."""
    circuit = Circuit(
        num_qubits=2,
        operations=(),
    )

    result = basis_state_permutation(circuit)

    assert result == (0, 1, 2, 3)


def test_basis_state_permutation_returns_pauli_x_permutation() -> None:
    """Return the basis-state permutation implemented by Pauli-X."""
    circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=X,
                qubits=(0,),
            ),
        ),
    )

    result = basis_state_permutation(circuit)

    assert result == (1, 0)


def test_basis_state_permutation_returns_identity_for_two_pauli_x_gates(
) -> None:
    """Return identity when Pauli-X is applied twice."""
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

    result = basis_state_permutation(circuit)

    assert result == (0, 1)


def test_basis_state_permutation_returns_cnot_permutation() -> None:
    """Return the little-endian permutation implemented by CNOT."""
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(
                gate=CNOT,
                qubits=(0, 1),
            ),
        ),
    )

    result = basis_state_permutation(circuit)

    assert result == (0, 3, 2, 1)


def test_basis_state_permutation_returns_toffoli_permutation() -> None:
    """Return the little-endian permutation implemented by Toffoli."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 2),
            ),
        ),
    )

    result = basis_state_permutation(circuit)

    assert result == (
        0,
        1,
        2,
        7,
        4,
        5,
        6,
        3,
    )


def test_basis_state_permutation_supports_reordered_toffoli_qubits() -> None:
    """Respect reordered Toffoli roles across the full permutation."""
    circuit = Circuit(
        num_qubits=4,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(3, 0, 2),
            ),
        ),
    )

    result = basis_state_permutation(circuit)

    expected = tuple(
        index ^ (1 << 2)
        if ((index >> 3) & 1) == 1
        and ((index >> 0) & 1) == 1
        else index
        for index in range(16)
    )

    assert result == expected


def test_basis_state_permutation_rejects_non_circuit_input() -> None:
    """Reject a circuit argument with the wrong type."""
    with pytest.raises(
        TypeError,
        match="circuit must be a Circuit object",
    ):
        basis_state_permutation(
            "not a circuit",  # type: ignore[arg-type]
        )


def test_basis_state_permutation_rejects_unsupported_gate() -> None:
    """Propagate unsupported-gate validation from basis-state simulation."""
    circuit = Circuit(
        num_qubits=1,
        operations=(
            Operation(
                gate=H,
                qubits=(0,),
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="does not support gate 'H'",
    ):
        basis_state_permutation(circuit)
