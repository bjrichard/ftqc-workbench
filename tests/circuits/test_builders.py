import random

import pytest

from qc_compiler.circuits import (
    Circuit,
    Operation,
    build_cuccaro_adder,
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


@pytest.mark.parametrize(
    ("controls", "target", "ancillas", "num_qubits"),
    [
        ((0,), 1, (), 2),
        ((0, 1), 2, (), 3),
        ((0, 1, 2), 3, (4,), 5),
        ((3, 0, 4, 1), 2, (5, 6), 7),
    ],
)
def test_multi_controlled_x_matches_clean_ancilla_truth_table(
    controls: tuple[int, ...],
    target: int,
    ancillas: tuple[int, ...],
    num_qubits: int,
) -> None:
    """Match the expected action on every clean-ancilla basis state."""
    circuit = build_multi_controlled_x(
        controls=controls,
        target=target,
        ancillas=ancillas,
        num_qubits=num_qubits,
    )

    for basis_index in range(2**num_qubits):
        ancillas_are_clean = all(
            ((basis_index >> ancilla) & 1) == 0
            for ancilla in ancillas
        )

        if not ancillas_are_clean:
            continue

        all_controls_are_one = all(
            ((basis_index >> control) & 1) == 1
            for control in controls
        )

        expected = (
            basis_index ^ (1 << target)
            if all_controls_are_one
            else basis_index
        )

        result = simulate_basis_state(circuit, basis_index)

        assert result == expected


@pytest.mark.parametrize("num_controls", [8, 16])
def test_large_multi_controlled_x_matches_random_clean_ancilla_inputs(
    num_controls: int,
) -> None:
    """Match expected behavior on randomized large clean-ancilla inputs."""
    controls = tuple(range(num_controls))
    target = num_controls
    ancillas = tuple(range(num_controls + 1, 2 * num_controls - 1))
    num_qubits = 2 * num_controls - 1

    circuit = build_multi_controlled_x(
        controls=controls,
        target=target,
        ancillas=ancillas,
        num_qubits=num_qubits,
    )

    rng = random.Random(20260706 + num_controls)

    for _ in range(100):
        basis_index = _random_clean_ancilla_basis_index(
            num_qubits=num_qubits,
            ancillas=ancillas,
            rng=rng,
        )

        expected = _expected_multi_controlled_x_result(
            basis_index=basis_index,
            controls=controls,
            target=target,
        )

        result = simulate_basis_state(circuit, basis_index)

        assert result == expected


def test_build_cuccaro_adder_with_one_bit_registers() -> None:
    """Build a CNOT for one-bit modular addition."""
    circuit = build_cuccaro_adder(
        a=(0,),
        b=(1,),
        carry=2,
        num_qubits=3,
    )

    expected = Circuit(
        num_qubits=3,
        operations=(
            Operation(
                gate=CNOT,
                qubits=(0, 1),
            ),
        ),
    )

    assert circuit == expected


@pytest.mark.parametrize("num_bits", [2, 3])
def test_build_cuccaro_adder_matches_truth_table(
    num_bits: int,
) -> None:
    """Match modular addition on every clean-carry basis state."""
    a = tuple(range(num_bits))
    b = tuple(range(num_bits, 2 * num_bits))
    carry = 2 * num_bits
    num_qubits = 2 * num_bits + 1

    circuit = build_cuccaro_adder(
        a=a,
        b=b,
        carry=carry,
        num_qubits=num_qubits,
    )

    for initial_a in range(2 ** len(a)):
        for initial_b in range(2 ** len(b)):
            basis_index = _basis_index_from_registers(
                a_value=initial_a,
                b_value=initial_b,
                a=a,
                b=b,
            )

            result = simulate_basis_state(circuit, basis_index)

            assert _register_value(result, a) == initial_a
            assert _register_value(result, b) == (
                initial_a + initial_b
            ) % (2 ** len(b))
            assert ((result >> carry) & 1) == 0


@pytest.mark.parametrize("num_bits", [4, 8, 16])
def test_large_cuccaro_adder_matches_random_clean_carry_inputs(
    num_bits: int,
) -> None:
    """Match modular addition on randomized large clean-carry inputs."""
    a = tuple(range(num_bits))
    b = tuple(range(num_bits, 2 * num_bits))
    carry = 2 * num_bits
    num_qubits = 2 * num_bits + 1

    circuit = build_cuccaro_adder(
        a=a,
        b=b,
        carry=carry,
        num_qubits=num_qubits,
    )

    rng = random.Random(20260710 + num_bits)

    for _ in range(100):
        initial_a = rng.randrange(2**num_bits)
        initial_b = rng.randrange(2**num_bits)

        basis_index = _basis_index_from_registers(
            a_value=initial_a,
            b_value=initial_b,
            a=a,
            b=b,
        )

        result = simulate_basis_state(circuit, basis_index)

        assert _register_value(result, a) == initial_a
        assert _register_value(result, b) == (
            initial_a + initial_b
        ) % (2**num_bits)
        assert ((result >> carry) & 1) == 0


@pytest.mark.parametrize(
    ("a", "b", "carry", "num_qubits", "error_type", "message"),
    [
        ([0], (1,), 2, 3, TypeError, "a must be a tuple."),
        ((0,), [1], 2, 3, TypeError, "b must be a tuple."),
        ((0,), (1,), True, 3, TypeError, "carry must be an integer."),
        ((0,), (1,), 2, True, TypeError, "num_qubits must be an integer."),
        ((True,), (1,), 2, 3, TypeError, "a qubit indices must be integers."),
        ((0,), (False,), 2, 3, TypeError, "b qubit indices must be integers."),
        ((), (), 0, 1, ValueError, "a and b must be nonempty."),
        ((0,), (1, 2), 3, 4, ValueError, "a and b must have equal length."),
        ((0, 0), (1, 2), 3, 4, ValueError, "a qubits must be distinct."),
        ((0, 1), (2, 2), 3, 4, ValueError, "b qubits must be distinct."),
        ((0,), (0,), 2, 3, ValueError, "a and b must be disjoint."),
        ((0,), (1,), 0, 3, ValueError, "carry must be distinct from a."),
        ((0,), (1,), 1, 3, ValueError, "carry must be distinct from b."),
        (
            (0,),
            (1,),
            3,
            3,
            ValueError,
            "Qubit index 3 is not in the quantum register.",
        ),
        (
            (-1,),
            (1,),
            2,
            3,
            ValueError,
            "Qubit index -1 is not in the quantum register.",
        ),
        ((0,), (1,), 2, 0, ValueError, "num_qubits must be positive."),
    ],
)
def test_build_cuccaro_adder_rejects_invalid_inputs(
    a: object,
    b: object,
    carry: object,
    num_qubits: object,
    error_type: type[Exception],
    message: str,
) -> None:
    """Reject invalid Cuccaro adder register specifications."""
    with pytest.raises(error_type, match=message):
        build_cuccaro_adder(
            a=a,  # type: ignore[arg-type]
            b=b,  # type: ignore[arg-type]
            carry=carry,  # type: ignore[arg-type]
            num_qubits=num_qubits,  # type: ignore[arg-type]
        )


def _expected_multi_controlled_x_result(
    basis_index: int,
    controls: tuple[int, ...],
    target: int,
) -> int:
    """Return the expected basis index after a multi-controlled Pauli-X."""
    all_controls_are_one = all(
        ((basis_index >> control) & 1) == 1
        for control in controls
    )

    return (
        basis_index ^ (1 << target)
        if all_controls_are_one
        else basis_index
    )


def _random_clean_ancilla_basis_index(
    *,
    num_qubits: int,
    ancillas: tuple[int, ...],
    rng: random.Random,
) -> int:
    """Generate a random basis index with every ancilla initialized to zero."""
    basis_index = rng.randrange(2**num_qubits)

    for ancilla in ancillas:
        basis_index &= ~(1 << ancilla)

    return basis_index


def _register_value(
    basis_index: int,
    register: tuple[int, ...],
) -> int:
    """Return the integer encoded by a little-endian qubit register."""
    value = 0

    for bit_position, qubit in enumerate(register):
        value |= ((basis_index >> qubit) & 1) << bit_position

    return value


def _basis_index_from_registers(
    *,
    a_value: int,
    b_value: int,
    a: tuple[int, ...],
    b: tuple[int, ...],
) -> int:
    """Return a basis index encoding little-endian a and b registers."""
    basis_index = 0

    for bit_position, qubit in enumerate(a):
        basis_index |= ((a_value >> bit_position) & 1) << qubit

    for bit_position, qubit in enumerate(b):
        basis_index |= ((b_value >> bit_position) & 1) << qubit

    return basis_index
