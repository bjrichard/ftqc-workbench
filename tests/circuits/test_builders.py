from qc_compiler.circuits import (
    Circuit,
    Operation,
    build_multi_controlled_x,
)
from qc_compiler.gates import CNOT, TOFFOLI
from qc_compiler.simulation import simulate_basis_state


def test_build_multi_controlled_x_with_one_control() -> None:
    """Build a CNOT for one control."""
    circuit = build_multi_controlled_x(
        controls=(0,),
        target=1,
        num_qubits=2,
    )

    expected = Circuit(
        num_qubits=2,
        operations=(
            Operation(
                gate=CNOT,
                qubits=(0, 1),
            ),
        ),
    )

    assert circuit == expected


def test_build_multi_controlled_x_with_two_controls() -> None:
    """Build a Toffoli gate for two controls."""
    circuit = build_multi_controlled_x(
        controls=(0, 1),
        target=2,
        num_qubits=3,
    )

    expected = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 2),
            ),
        ),
    )

    assert circuit == expected


def test_build_multi_controlled_x_with_three_controls() -> None:
    """Build a compute-use-uncompute ladder for three controls."""
    circuit = build_multi_controlled_x(
        controls=(0, 1, 2),
        target=3,
        ancillas=(4,),
        num_qubits=5,
    )

    expected = Circuit(
        num_qubits=5,
        operations=(
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 4),
            ),
            Operation(
                gate=TOFFOLI,
                qubits=(4, 2, 3),
            ),
            Operation(
                gate=TOFFOLI,
                qubits=(0, 1, 4),
            ),
        ),
    )

    assert circuit == expected


def test_multi_controlled_x_flips_target_when_all_controls_are_one() -> None:
    """Flip the target when every control is one."""
    circuit = build_multi_controlled_x(
        controls=(0, 1, 2),
        target=3,
        ancillas=(4,),
        num_qubits=5,
    )

    initial_index = 0b00111
    result = simulate_basis_state(circuit, initial_index)

    assert result == 0b01111
