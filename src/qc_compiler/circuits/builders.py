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
        operations = (
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
