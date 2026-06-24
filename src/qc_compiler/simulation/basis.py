from __future__ import annotations

from qc_compiler.circuits import Circuit
from qc_compiler.gates import CNOT, I, TOFFOLI, X


def simulate_basis_state(
    circuit: Circuit,
    basis_index: int,
) -> int:
    """Simulate a circuit on a computational-basis state.

    Parameters
    ----------
    circuit
        Circuit containing only gates supported by basis-state simulation.
    basis_index
        Integer index of the initial computational-basis state.

    Returns
    -------
    int
        Integer index of the final computational-basis state.

    Raises
    ------
    TypeError
        If ``circuit`` is not a ``Circuit`` or ``basis_index`` is not an
        integer.
    ValueError
        If ``basis_index`` is outside the circuit register or the circuit
        contains a gate that is not supported by basis-state simulation.

    Notes
    -----
    Basis indices use little-endian qubit indexing: qubit zero is the least
    significant bit.

    The order of ``operation.qubits`` defines gate roles. For Controlled-NOT
    (CNOT), the tuple is ``(control, target)``. For Toffoli, the tuple is
    ``(control_0, control_1, target)``.

    This simulator supports only gates that map each computational-basis
    state to exactly one computational-basis state. It does not track
    amplitudes or phases.
    """
    if not isinstance(circuit, Circuit):
        raise TypeError("circuit must be a Circuit object.")

    if isinstance(basis_index, bool) or not isinstance(basis_index, int):
        raise TypeError("basis_index must be an integer.")

    state_dimension = 2**circuit.num_qubits

    if not 0 <= basis_index < state_dimension:
        raise ValueError(
            "basis_index must satisfy "
            f"0 <= basis_index < {state_dimension}."
        )

    output_index = basis_index

    for operation in circuit.operations:
        if operation.gate == I:
            continue

        if operation.gate == X:
            (target,) = operation.qubits
            output_index ^= 1 << target
            continue

        if operation.gate == CNOT:
            control, target = operation.qubits
            control_bit = (output_index >> control) & 1

            if control_bit == 1:
                output_index ^= 1 << target

            continue

        if operation.gate == TOFFOLI:
            control_0, control_1, target = operation.qubits
            control_bit_0 = (output_index >> control_0) & 1
            control_bit_1 = (output_index >> control_1) & 1

            if control_bit_0 == 1 and control_bit_1 == 1:
                output_index ^= 1 << target

            continue

        raise ValueError(
            "Basis-state simulation does not support "
            f"gate {operation.gate.name!r}."
        )

    return output_index


def basis_state_permutation(
    circuit: Circuit,
) -> tuple[int, ...]:
    """Return the basis-state permutation implemented by a circuit.

    Parameters
    ----------
    circuit
        Circuit containing only gates supported by basis-state simulation.

    Returns
    -------
    tuple[int, ...]
        Output basis index for each computational-basis input. Entry ``j``
        contains the output produced from input basis index ``j``.

    Raises
    ------
    TypeError
        If ``circuit`` is not a ``Circuit``.
    ValueError
        If the circuit contains a gate that is not supported by basis-state
        simulation.

    Notes
    -----
    The returned tuple has length ``2**circuit.num_qubits``. Input and output
    indices use little-endian qubit indexing.

    Because every supported gate is reversible, the returned values form a
    permutation of the integers from ``0`` through
    ``2**circuit.num_qubits - 1``.
    """
    if not isinstance(circuit, Circuit):
        raise TypeError("circuit must be a Circuit object.")

    state_dimension = 2**circuit.num_qubits

    return tuple(
        simulate_basis_state(
            circuit=circuit,
            basis_index=basis_index,
        )
        for basis_index in range(state_dimension)
    )
