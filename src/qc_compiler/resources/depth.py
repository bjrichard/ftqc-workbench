from __future__ import annotations

from qc_compiler.circuits import Circuit


def estimate_parallel_depth(circuit: Circuit) -> int:
    """Estimate greedy parallelized circuit depth.

    Parameters
    ----------
    circuit : Circuit
        Circuit whose operations should be assigned to parallel layers.

    Returns
    -------
    int
        Number of greedy parallel layers required by the circuit.

    Raises
    ------
    TypeError
        If ``circuit`` is not a Circuit object.

    Notes
    -----
    This function preserves operation order. It places each operation into the
    earliest existing layer that has no qubit conflict. It does not commute,
    reorder, route, or globally optimize the circuit.
    """
    if not isinstance(circuit, Circuit):
        raise TypeError("circuit must be a Circuit object.")

    layers: list[set[int]] = []

    for operation in circuit:
        operation_qubits = set(operation.qubits)
        placed = False

        for layer_qubits in layers:
            if operation_qubits.isdisjoint(layer_qubits):
                layer_qubits.update(operation_qubits)
                placed = True
                break

        if not placed:
            layers.append(operation_qubits)

    return len(layers)
