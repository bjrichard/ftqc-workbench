from __future__ import annotations

from dataclasses import dataclass

from qc_compiler.gates import Gate


@dataclass(frozen=True)
class Operation:
    """Application of a logical gate to concrete qubit indices.

    An operation binds an abstract Gate to the specific qubit indices it
    acts on inside a circuit. The order of qubit indices follows the gate
    convention.

    Parameters
    ----------
    gate : Gate
        Logical gate definition to apply.
    qubits : tuple[int, ...]
        Zero-based qubit indices the gate acts on.

    Raises
    ------
    TypeError
        If ``gate`` is not a Gate object.
    TypeError
        If ``qubits`` is not a tuple or contains non-integer entries.
    ValueError
        If any qubit index is negative.
    ValueError
        If duplicate qubit indices are provided.
    ValueError
        If the number of qubit indices does not match the gate arity.
    """

    gate: Gate
    qubits: tuple[int, ...]

    def __post_init__(self) -> None:
        """Validate operation invariants after dataclass initialization."""
        if not isinstance(self.gate, Gate):
            raise TypeError("gate must be a Gate object.")

        if not isinstance(self.qubits, tuple):
            raise TypeError("qubits must be a tuple.")

        for qubit in self.qubits:
            if not isinstance(qubit, int):
                raise TypeError("qubit indices must be integers.")

            if qubit < 0:
                raise ValueError("qubit indices must be non-negative.")

        if len(self.qubits) != len(set(self.qubits)):
            raise ValueError("qubits cannot contain duplicate indices.")

        if len(self.qubits) != self.gate.arity:
            raise ValueError("number of qubits must equal gate arity.")
