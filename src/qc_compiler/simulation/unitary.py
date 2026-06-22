from __future__ import annotations

import numpy as np

from qc_compiler.circuits import Circuit
from qc_compiler.simulation import simulate_statevector


def circuit_to_unitary(circuit: Circuit) -> np.ndarray:
    """
    Construct the unitary matrix represented by a circuit.

    Parameters
    ----------
    circuit : Circuit
        Circuit whose operations are applied in order.

    Returns
    -------
    np.ndarray
        Complex unitary matrix with shape ``(2**n, 2**n)``, where
        ``n`` is the circuit register size. Column ``j`` is the final
        statevector obtained by simulating the circuit from computational
        basis state ``|j>``.

    Raises
    ------
    TypeError
        If ``circuit`` is not a ``Circuit``.

    Notes
    -----
    Computational-basis indices follow the simulator's little-endian
    convention, with qubit zero represented by the least significant bit.
    """
    if not isinstance(circuit, Circuit):
        raise TypeError("circuit must be a Circuit object.")

    dimension = 2**circuit.num_qubits
    unitary = np.zeros(
        (dimension, dimension),
        dtype=complex,
    )

    for basis_index in range(dimension):
        initial_statevector = np.zeros(
            dimension,
            dtype=complex,
        )
        initial_statevector[basis_index] = 1

        unitary[:, basis_index] = simulate_statevector(
            circuit=circuit,
            initial_statevector=initial_statevector,
        )

    return unitary
