"""Utilities for applying quantum operations to statevectors."""

from __future__ import annotations

import math

import numpy as np

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.simulation.matrices import get_gate_matrix


def apply_operation_to_statevector(
    operation: Operation,
    statevector: np.ndarray,
) -> np.ndarray:
    """
    Apply one quantum operation to a full statevector.

    The statevector uses little-endian computational-basis indexing:
    qubit ``q`` corresponds to bit position ``q`` in each basis-state
    index. The order of ``operation.qubits`` defines the local basis
    ordering of the gate matrix. The first operation qubit corresponds
    to local bit position zero.

    The input statevector is not modified.

    Parameters
    ----------
    operation : Operation
        Quantum operation to apply.
    statevector : np.ndarray
        One-dimensional statevector with power-of-two length.

    Returns
    -------
    np.ndarray
        New statevector obtained after applying the operation.

    Raises
    ------
    TypeError
        If ``operation`` is not an ``Operation`` or ``statevector`` is
        not a NumPy array.
    ValueError
        If the statevector is not one-dimensional, is empty, does not
        have power-of-two length, or is too small for a targeted qubit.
    """
    if not isinstance(operation, Operation):
        raise TypeError("operation must be an Operation.")

    if not isinstance(statevector, np.ndarray):
        raise TypeError("statevector must be a NumPy array.")

    num_qubits = _infer_num_qubits(statevector)

    if any(qubit >= num_qubits for qubit in operation.qubits):
        raise ValueError(
            "Operation targets a qubit outside the statevector."
        )

    gate_matrix = get_gate_matrix(operation.gate)
    result = np.zeros(statevector.shape, dtype=complex)

    for input_basis_index in range(statevector.size):
        input_amplitude = statevector[input_basis_index]

        if input_amplitude == 0:
            continue

        local_input_index = _extract_local_index(
            input_basis_index,
            operation.qubits,
        )

        for local_output_index in range(gate_matrix.shape[0]):
            coefficient = gate_matrix[
                local_output_index,
                local_input_index,
            ]

            if coefficient == 0:
                continue

            output_basis_index = _replace_local_bits(
                input_basis_index,
                operation.qubits,
                local_output_index,
            )

            result[output_basis_index] += (
                coefficient * input_amplitude
            )

    return result


def _infer_num_qubits(statevector: np.ndarray) -> int:
    """
    Infer the number of qubits represented by a statevector.

    Parameters
    ----------
    statevector : np.ndarray
        Statevector whose length should equal ``2**num_qubits``.

    Returns
    -------
    int
        Number of qubits represented by the statevector.

    Raises
    ------
    ValueError
        If the statevector is not one-dimensional, is empty, or does
        not have power-of-two length.
    """
    if statevector.ndim != 1:
        raise ValueError("Statevector must be one-dimensional.")

    size = statevector.size

    if size == 0:
        raise ValueError("Statevector must be nonempty.")

    num_qubits = math.log2(size)

    if not num_qubits.is_integer():
        raise ValueError(
            "Statevector length must be a power of two."
        )

    return int(num_qubits)


def _get_bit(index: int, position: int) -> int:
    """
    Return the bit at a specified position in an integer.

    Parameters
    ----------
    index : int
        Nonnegative integer encoding a computational-basis state.
    position : int
        Zero-based bit position to inspect.

    Returns
    -------
    int
        Bit value, either zero or one.
    """
    return (index >> position) & 1


def _extract_local_index(
    basis_index: int,
    qubits: tuple[int, ...],
) -> int:
    """
    Pack selected full-register bits into a local basis index.

    The qubit at ``qubits[0]`` becomes local bit position zero,
    ``qubits[1]`` becomes local bit position one, and so forth.

    Parameters
    ----------
    basis_index : int
        Full-register computational-basis index.
    qubits : tuple[int, ...]
        Full-register qubit positions to extract.

    Returns
    -------
    int
        Local computational-basis index formed from the selected bits.
    """
    local_index = 0

    for local_position, qubit in enumerate(qubits):
        bit = _get_bit(basis_index, qubit)
        local_index += bit << local_position

    return local_index


def _replace_local_bits(
    basis_index: int,
    qubits: tuple[int, ...],
    local_index: int,
) -> int:
    """
    Replace selected full-register bits with local-index bits.

    The bit at local position zero replaces the qubit at
    ``qubits[0]``, the bit at local position one replaces the qubit at
    ``qubits[1]``, and so forth. All other full-register bits remain
    unchanged.

    Parameters
    ----------
    basis_index : int
        Original full-register computational-basis index.
    qubits : tuple[int, ...]
        Full-register qubit positions to replace.
    local_index : int
        Local basis index supplying the replacement bits.

    Returns
    -------
    int
        Full-register basis index containing the replacement bits.
    """
    output_basis_index = basis_index

    for local_position, qubit in enumerate(qubits):
        bit = _get_bit(local_index, local_position)
        output_basis_index = _set_bit(
            output_basis_index,
            qubit,
            bit,
        )

    return output_basis_index


def _set_bit(
    index: int,
    position: int,
    bit: int,
) -> int:
    """
    Return an integer with one bit replaced.

    Parameters
    ----------
    index : int
        Integer whose bit should be replaced.
    position : int
        Zero-based position of the bit to replace.
    bit : int
        Replacement value, either zero or one.

    Returns
    -------
    int
        Integer with the requested bit value.

    Raises
    ------
    ValueError
        If ``bit`` is not zero or one.
    """
    if bit not in (0, 1):
        raise ValueError("bit must be zero or one.")

    if bit == 0:
        return index & ~(1 << position)

    return index | (1 << position)


def simulate_statevector(
    circuit: Circuit,
    initial_statevector: np.ndarray | None = None,
) -> np.ndarray:
    """
    Simulate a circuit and return the final statevector.

    Parameters
    ----------
    circuit : Circuit
        Circuit whose operations are applied in order.
    initial_statevector : np.ndarray | None, optional
        Initial statevector. If omitted, the simulation begins in the
        all-zero computational basis state.

    Returns
    -------
    np.ndarray
        Final complex-valued statevector.

    Raises
    ------
    TypeError
        If ``circuit`` is not a ``Circuit`` or ``initial_statevector`` is
        not a NumPy array.
    ValueError
        If the initial statevector is not one-dimensional or has the wrong
        size for the circuit register.
    """
    if not isinstance(circuit, Circuit):
        raise TypeError("circuit must be a Circuit object.")

    num_qubits = circuit.num_qubits
    expected_size = 2**num_qubits

    if initial_statevector is None:
        statevector = np.zeros(
            expected_size,
            dtype=complex,
        )
        statevector[0] = 1

    else:
        if not isinstance(initial_statevector, np.ndarray):
            raise TypeError(
                "initial_statevector must be a NumPy array."
            )

        if initial_statevector.ndim != 1:
            raise ValueError(
                "Initial statevector must be one-dimensional."
            )

        if initial_statevector.size != expected_size:
            raise ValueError(
                "Initial statevector size must match the circuit "
                "register size."
            )

        statevector = initial_statevector.astype(
            complex,
            copy=True,
        )

    for operation in circuit.operations:
        statevector = apply_operation_to_statevector(
            operation=operation,
            statevector=statevector,
        )

    return statevector
