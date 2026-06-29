from __future__ import annotations

from qc_compiler.circuits import Circuit


def estimate_parallel_depth(circuit: Circuit) -> int:
    """Estimate circuit depth while preserving qubit dependencies.

    Parameters
    ----------
    circuit
        Circuit whose parallel depth should be estimated.

    Returns
    -------
    int
        Number of dependency-preserving execution layers.

    Raises
    ------
    TypeError
        If ``circuit`` is not a ``Circuit`` object.

    Notes
    -----
    Operations acting on disjoint qubits may share a layer. Operations sharing
    any qubit are ordered according to their appearance in the circuit.
    """
    if not isinstance(circuit, Circuit):
        raise TypeError("circuit must be a Circuit object.")

    last_layer_by_qubit = [0] * circuit.num_qubits
    depth = 0

    for operation in circuit.operations:
        operation_layer = (
            max(
                last_layer_by_qubit[qubit]
                for qubit in operation.qubits
            )
            + 1
        )

        for qubit in operation.qubits:
            last_layer_by_qubit[qubit] = operation_layer

        depth = max(depth, operation_layer)

    return depth
