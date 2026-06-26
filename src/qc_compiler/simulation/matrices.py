from __future__ import annotations

import numpy as np

from qc_compiler.gates.gate import Gate
from qc_compiler.gates.library import (
    CNOT,
    CZ,
    H,
    I,
    S,
    T,
    TOFFOLI,
    X,
    Y,
    Z,
)


_GATE_MATRICES: dict[Gate, np.ndarray] = {
    I: np.array(
        [
            [1, 0],
            [0, 1],
        ],
        dtype=complex,
    ),
    X: np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=complex,
    ),
    Y: np.array(
        [
            [0, -1j],
            [1j, 0],
        ],
        dtype=complex,
    ),
    Z: np.array(
        [
            [1, 0],
            [0, -1],
        ],
        dtype=complex,
    ),
    H: (1 / np.sqrt(2))
    * np.array(
        [
            [1, 1],
            [1, -1],
        ],
        dtype=complex,
    ),
    S: np.array(
        [
            [1, 0],
            [0, 1j],
        ],
        dtype=complex,
    ),
    T: np.array(
        [
            [1, 0],
            [0, np.exp(1j * np.pi / 4)],
        ],
        dtype=complex,
    ),
    CNOT: np.array(
        [
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
        ],
        dtype=complex,
    ),
    CZ: np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, -1],
        ],
        dtype=complex,
    ),
    TOFFOLI: np.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
        ],
        dtype=complex,
    ),
}


def get_gate_matrix(gate: Gate) -> np.ndarray:
    """Return the matrix representation of a primitive gate.

    Parameters
    ----------
    gate : Gate
        Primitive gate whose matrix should be returned.

    Returns
    -------
    np.ndarray
        Complex-valued matrix representation of the gate.

    Raises
    ------
    TypeError
        If ``gate`` is not a Gate object.
    ValueError
        If ``gate`` does not have a supported matrix representation.

    Notes
    -----
    Matrices follow the little-endian statevector convention documented in
    ``docs/simulation_conventions.md``. Returned matrices are copies so callers
    cannot mutate the internal matrix table.
    """
    if not isinstance(gate, Gate):
        raise TypeError("gate must be a Gate object.")

    if gate not in _GATE_MATRICES:
        raise ValueError(f"unsupported gate matrix: {gate.name}")

    return _GATE_MATRICES[gate].copy()
