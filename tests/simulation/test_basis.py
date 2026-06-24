from __future__ import annotations

import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, H, I, X
from qc_compiler.simulation.basis import simulate_basis_state


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


def test_x_flips_target_bit() -> None:
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


def test_operations_are_applied_in_order() -> None:
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(
                gate=X,
                qubits=(0,),
            ),
            Operation(
                gate=CNOT,
                qubits=(0, 1),
            ),
        ),
    )

    result = simulate_basis_state(
        circuit=circuit,
        basis_index=0b00,
    )

    assert result == 0b11


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

    with pytest.raises(ValueError):
        simulate_basis_state(
            circuit=circuit,
            basis_index=0,
        )
