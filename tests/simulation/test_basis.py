from __future__ import annotations

import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, H, I, TOFFOLI, X
from qc_compiler.simulation import simulate_basis_state


def test_identity_leaves_basis_index_unchanged() -> None:
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
    circuit = Circuit(
        num_qubits=2,
        operations=(),
    )

    with pytest.raises(ValueError):
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
    circuit = Circuit(
        num_qubits=2,
        operations=(),
    )

    with pytest.raises(TypeError):
        simulate_basis_state(
            circuit=circuit,
            basis_index=basis_index,
        )


def test_non_circuit_input_raises_type_error() -> None:
    with pytest.raises(TypeError):
        simulate_basis_state(
            circuit="not a circuit",
            basis_index=0,
        )


def test_unsupported_gate_raises_value_error() -> None:
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
