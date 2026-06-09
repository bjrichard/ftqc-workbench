from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceEstimate:
    """Logical resource estimate for a circuit.

    A resource estimate stores scalar logical resource counts computed from a
    circuit. It is a data object only; estimator logic belongs in
    ResourceEstimator.

    Parameters
    ----------
    gate_count : int
        Total number of logical gates.
    t_count : int
        Number of T gates.
    cnot_count : int
        Number of controlled-NOT gates.
    cz_count : int
        Number of controlled-Z gates.
    logical_qubit_count : int
        Number of logical qubits represented by the circuit.
    ancilla_count : int
        Number of ancilla qubits required by the estimate.
    depth : int | None
        Estimated circuit depth, or None if no depth model has been applied.

    Raises
    ------
    TypeError
        If any count is not an integer.
    TypeError
        If ``depth`` is neither an integer nor None.
    ValueError
        If any count is negative.
    ValueError
        If ``depth`` is negative.
    """

    gate_count: int
    t_count: int
    cnot_count: int
    cz_count: int
    logical_qubit_count: int
    ancilla_count: int = 0
    depth: int | None = None

    def __post_init__(self) -> None:
        """Validate resource estimate invariants after dataclass initialization."""
        self._validate_nonnegative_integer("gate_count", self.gate_count)
        self._validate_nonnegative_integer("t_count", self.t_count)
        self._validate_nonnegative_integer("cnot_count", self.cnot_count)
        self._validate_nonnegative_integer("cz_count", self.cz_count)
        self._validate_nonnegative_integer(
            "logical_qubit_count", self.logical_qubit_count
        )
        self._validate_nonnegative_integer("ancilla_count", self.ancilla_count)

        if self.depth is not None:
            self._validate_nonnegative_integer("depth", self.depth)

    @staticmethod
    def _validate_nonnegative_integer(name: str, value: int) -> None:
        """Validate that a value is a nonnegative integer."""
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer.")

        if value < 0:
            raise ValueError(f"{name} must be nonnegative.")
