from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Gate:
    """Logical quantum gate definition.

    A gate describes the abstract operation type, not where it is applied
    in a circuit. Concrete qubit indices are supplied by an Operation.

    Parameters
    ----------
    name : str
        Human-readable gate name.
    arity : int
        Number of qubits the gate acts on.

    Raises
    ------
    ValueError
        If ``name`` is not a non-empty string.
    ValueError
        If ``arity`` is not a positive integer.
    """

    name: str
    arity: int

    def __post_init__(self) -> None:
        """Validate gate invariants after dataclass initialization."""
        if not isinstance(self.name, str):
            raise ValueError("Gate name must be a string.")

        if not self.name.strip():
            raise ValueError("Gate name must be non-empty.")

        if not isinstance(self.arity, int):
            raise ValueError("Gate arity must be an integer.")

        if self.arity < 1:
            raise ValueError("Gate arity must be positive.")
