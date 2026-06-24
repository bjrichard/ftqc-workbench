from __future__ import annotations

from qc_compiler.circuits import Circuit
from qc_compiler.gates import CNOT, I, X


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

        raise ValueError(
            "Basis-state simulation does not support "
            f"gate {operation.gate.name!r}."
        )

    return output_index
