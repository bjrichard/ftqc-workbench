from __future__ import annotations

from qc_compiler.circuits.circuit import Circuit
from qc_compiler.circuits.operation import Operation
from qc_compiler.gates import CNOT, TOFFOLI


def build_multi_controlled_x(
    controls: tuple[int, ...],
    target: int,
    ancillas: tuple[int, ...] = (),
    *,
    num_qubits: int,
) -> Circuit:
    """Construct a multi-controlled Pauli-X circuit.

    Parameters
    ----------
    controls
        Ordered tuple of distinct control-qubit indices.
    target
        Target-qubit index.
    ancillas
        Ordered tuple of distinct clean ancilla-qubit indices. For three or
        more controls, exactly ``len(controls) - 2`` ancillas are required.
    num_qubits
        Number of qubits in the circuit register.

    Returns
    -------
    Circuit
        Circuit implementing a Pauli-X operation on ``target`` controlled by
        every qubit in ``controls``.

    Raises
    ------
    TypeError
        If an argument has the wrong type or if any qubit index is a Boolean.
    ValueError
        If the register size or a qubit index is invalid, if qubit roles
        overlap, or if the wrong number of ancillas is supplied.

    Notes
    -----
    For one control, the circuit contains a Controlled-NOT (CNOT) gate. For
    two controls, it contains a Toffoli gate. For three or more controls, it
    uses a clean-ancilla Toffoli ladder and restores every ancilla to zero.

    The ancillas are assumed to begin in the computational basis state
    ``|0>``.
    """
    if not isinstance(controls, tuple):
        raise TypeError("controls must be a tuple.")

    if not isinstance(ancillas, tuple):
        raise TypeError("ancillas must be a tuple.")

    if isinstance(target, bool) or not isinstance(target, int):
        raise TypeError("target must be an integer.")

    if isinstance(num_qubits, bool) or not isinstance(num_qubits, int):
        raise TypeError("num_qubits must be an integer.")

    if num_qubits <= 0:
        raise ValueError("num_qubits must be positive.")

    if len(controls) == 0:
        raise ValueError("controls must contain at least one qubit.")

    for control in controls:
        if isinstance(control, bool) or not isinstance(control, int):
            raise TypeError("Control qubit indices must be integers.")

    for ancilla in ancillas:
        if isinstance(ancilla, bool) or not isinstance(ancilla, int):
            raise TypeError("Ancilla qubit indices must be integers.")

    if len(set(controls)) != len(controls):
        raise ValueError("Controls must be distinct.")

    if len(set(ancillas)) != len(ancillas):
        raise ValueError("Ancillas must be distinct.")

    all_indices = (*controls, target, *ancillas)

    for qubit in all_indices:
        if not 0 <= qubit < num_qubits:
            raise ValueError(
                f"Qubit index {qubit} is not in the quantum register."
            )

    if target in controls:
        raise ValueError("target must be distinct from all controls.")

    if target in ancillas:
        raise ValueError("target must be distinct from all ancillas.")

    if set(controls) & set(ancillas):
        raise ValueError("Controls and ancillas must be disjoint.")

    num_controls = len(controls)
    required_ancillas = max(0, num_controls - 2)

    if len(ancillas) != required_ancillas:
        raise ValueError(
            f"{required_ancillas} ancillas are required for "
            f"{num_controls} controls."
        )

    if num_controls == 1:
        operations: tuple[Operation, ...] = (
            Operation(
                gate=CNOT,
                qubits=(controls[0], target),
            ),
        )

        return Circuit(
            num_qubits=num_qubits,
            operations=operations,
        )

    if num_controls == 2:
        operations = (
            Operation(
                gate=TOFFOLI,
                qubits=(controls[0], controls[1], target),
            ),
        )

        return Circuit(
            num_qubits=num_qubits,
            operations=operations,
        )

    compute_operations: list[Operation] = []

    compute_operations.append(
        Operation(
            gate=TOFFOLI,
            qubits=(controls[0], controls[1], ancillas[0]),
        )
    )

    for ancilla_index in range(1, required_ancillas):
        compute_operations.append(
            Operation(
                gate=TOFFOLI,
                qubits=(
                    ancillas[ancilla_index - 1],
                    controls[ancilla_index + 1],
                    ancillas[ancilla_index],
                ),
            )
        )

    target_operation = Operation(
        gate=TOFFOLI,
        qubits=(
            ancillas[-1],
            controls[-1],
            target,
        ),
    )

    operations = (
        *compute_operations,
        target_operation,
        *reversed(compute_operations),
    )

    return Circuit(
        num_qubits=num_qubits,
        operations=operations,
    )


def build_cuccaro_adder(
    a: tuple[int, ...],
    b: tuple[int, ...],
    carry: int,
    *,
    num_qubits: int,
) -> Circuit:
    """Construct a Cuccaro-style in-place ripple-carry adder.

    Parameters
    ----------
    a
        Ordered tuple of distinct qubit indices for the preserved input
        register. The tuple position gives the register bit position, with
        ``a[0]`` interpreted as the least-significant bit.
    b
        Ordered tuple of distinct qubit indices for the register overwritten
        by the modular sum. The tuple position gives the register bit
        position, with ``b[0]`` interpreted as the least-significant bit.
    carry
        Clean work-qubit index. The qubit is assumed to begin in ``|0>`` and
        is restored to ``|0>``.
    num_qubits
        Number of qubits in the circuit register.

    Returns
    -------
    Circuit
        Circuit implementing in-place modular addition,

        ``|a>|b>|0> -> |a>|a + b mod 2**n>|0>``,

        for equal-width input registers.

    Raises
    ------
    TypeError
        If an argument has the wrong type or if any qubit index is a Boolean.
    ValueError
        If register sizes are invalid, qubit roles overlap, or any qubit index
        is outside the circuit register.

    Notes
    -----
    The one-bit and two-bit cases use compact specialized circuits. For three
    or more bits, the implementation uses Cuccaro-style majority and
    unmajority-and-add blocks.

    The implementation is modular: it discards the final overflow bit and
    writes the result modulo ``2**len(b)`` into ``b``.
    """
    if not isinstance(a, tuple):
        raise TypeError("a must be a tuple.")

    if not isinstance(b, tuple):
        raise TypeError("b must be a tuple.")

    if isinstance(carry, bool) or not isinstance(carry, int):
        raise TypeError("carry must be an integer.")

    if isinstance(num_qubits, bool) or not isinstance(num_qubits, int):
        raise TypeError("num_qubits must be an integer.")

    if num_qubits <= 0:
        raise ValueError("num_qubits must be positive.")

    if len(a) == 0 or len(b) == 0:
        raise ValueError("a and b must be nonempty.")

    if len(a) != len(b):
        raise ValueError("a and b must have equal length.")

    for qubit in a:
        if isinstance(qubit, bool) or not isinstance(qubit, int):
            raise TypeError("a qubit indices must be integers.")

    for qubit in b:
        if isinstance(qubit, bool) or not isinstance(qubit, int):
            raise TypeError("b qubit indices must be integers.")

    if len(set(a)) != len(a):
        raise ValueError("a qubits must be distinct.")

    if len(set(b)) != len(b):
        raise ValueError("b qubits must be distinct.")

    if set(a) & set(b):
        raise ValueError("a and b must be disjoint.")

    if carry in a:
        raise ValueError("carry must be distinct from a.")

    if carry in b:
        raise ValueError("carry must be distinct from b.")

    for qubit in (*a, *b, carry):
        if not 0 <= qubit < num_qubits:
            raise ValueError(
                f"Qubit index {qubit} is not in the quantum register."
            )

    if len(a) == 1:
        return Circuit(
            num_qubits=num_qubits,
            operations=(
                Operation(
                    gate=CNOT,
                    qubits=(a[0], b[0]),
                ),
            ),
        )

    if len(a) == 2:
        return Circuit(
            num_qubits=num_qubits,
            operations=(
                Operation(
                    gate=TOFFOLI,
                    qubits=(a[0], b[0], b[1]),
                ),
                Operation(
                    gate=CNOT,
                    qubits=(a[1], b[1]),
                ),
                Operation(
                    gate=CNOT,
                    qubits=(a[0], b[0]),
                ),
            ),
        )

    operations: list[Operation] = []

    _append_majority(
        operations=operations,
        carry=carry,
        b=b[0],
        a=a[0],
    )

    for bit_index in range(1, len(a)):
        _append_majority(
            operations=operations,
            carry=a[bit_index - 1],
            b=b[bit_index],
            a=a[bit_index],
        )

    for bit_index in reversed(range(1, len(a))):
        _append_unmajority_and_add(
            operations=operations,
            carry=a[bit_index - 1],
            b=b[bit_index],
            a=a[bit_index],
        )

    _append_unmajority_and_add(
        operations=operations,
        carry=carry,
        b=b[0],
        a=a[0],
    )

    return Circuit(
        num_qubits=num_qubits,
        operations=tuple(operations),
    )


def _append_majority(
    operations: list[Operation],
    carry: int,
    b: int,
    a: int,
) -> None:
    """Append a Cuccaro majority block.

    Parameters
    ----------
    operations
        Mutable operation list receiving the majority block.
    carry
        Qubit currently storing the incoming carry bit.
    b
        Qubit storing the current bit of the overwritten addend register.
    a
        Qubit storing the current bit of the preserved addend register.

    Returns
    -------
    None
        The function mutates ``operations`` in place.

    Notes
    -----
    The block maps the outgoing carry into the ``a`` line. In the ripple
    sequence, that line is then used as the carry input for the next more
    significant bit.
    """
    operations.append(
        Operation(
            gate=CNOT,
            qubits=(a, b),
        )
    )
    operations.append(
        Operation(
            gate=CNOT,
            qubits=(a, carry),
        )
    )
    operations.append(
        Operation(
            gate=TOFFOLI,
            qubits=(carry, b, a),
        )
    )


def _append_unmajority_and_add(
    operations: list[Operation],
    carry: int,
    b: int,
    a: int,
) -> None:
    """Append a Cuccaro unmajority-and-add block.

    Parameters
    ----------
    operations
        Mutable operation list receiving the unmajority-and-add block.
    carry
        Qubit storing the incoming carry for this bit position.
    b
        Qubit storing the current bit of the overwritten addend register.
    a
        Qubit storing the current bit of the preserved addend register.

    Returns
    -------
    None
        The function mutates ``operations`` in place.

    Notes
    -----
    The block reverses the corresponding majority computation, restores the
    ``a`` line, and writes the sum bit into the ``b`` line.
    """
    operations.append(
        Operation(
            gate=TOFFOLI,
            qubits=(carry, b, a),
        )
    )
    operations.append(
        Operation(
            gate=CNOT,
            qubits=(a, carry),
        )
    )
    operations.append(
        Operation(
            gate=CNOT,
            qubits=(carry, b),
        )
    )
