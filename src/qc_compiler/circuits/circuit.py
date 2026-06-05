from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from qc_compiler.circuits.operation import Operation
from qc_compiler.gates import Gate


@dataclass(frozen=True)
class Circuit:
    """Ordered sequence of operations on a fixed number of qubits.

    A circuit stores a fixed qubit count and an ordered tuple of operations.
    Appending an operation returns a new circuit rather than mutating the
    existing circuit.

    Parameters
    ----------
    num_qubits : int
        Number of qubits in the circuit.
    operations : tuple[Operation, ...]
        Ordered operations in the circuit.

    Raises
    ------
    TypeError
        If ``num_qubits`` is not an integer.
    TypeError
        If ``operations`` is not a tuple.
    TypeError
        If ``operations`` contains non-Operation entries.
    ValueError
        If ``num_qubits`` is not positive.
    ValueError
        If any operation uses a qubit index outside the circuit.
    """

    num_qubits: int
    operations: tuple[Operation, ...] = ()

    def __post_init__(self) -> None:
        """Validate circuit invariants after dataclass initialization."""
        if not isinstance(self.num_qubits, int):
            raise TypeError("num_qubits must be an integer.")

        if self.num_qubits <= 0:
            raise ValueError("num_qubits must be positive.")

        if not isinstance(self.operations, tuple):
            raise TypeError("operations must be a tuple.")

        for operation in self.operations:
            if not isinstance(operation, Operation):
                raise TypeError("operations must contain only Operation objects.")

            self._validate_operation_qubits(operation)

    def append(self, operation: Operation) -> Circuit:
        """Return a new circuit with one operation appended.

        Parameters
        ----------
        operation : Operation
            Operation to append to the circuit.

        Returns
        -------
        Circuit
            New circuit containing the existing operations followed by the
            appended operation.

        Raises
        ------
        TypeError
            If ``operation`` is not an Operation object.
        ValueError
            If ``operation`` uses a qubit index outside the circuit.
        """
        if not isinstance(operation, Operation):
            raise TypeError("operation must be an Operation object.")

        self._validate_operation_qubits(operation)

        return Circuit(
            num_qubits=self.num_qubits,
            operations=self.operations + (operation,),
        )

    def append_gate(self, gate: Gate, qubits: tuple[int, ...]) -> Circuit:
        """Return a new circuit with one gate applied to qubits.

        Parameters
        ----------
        gate : Gate
            Logical gate definition to apply.
        qubits : tuple[int, ...]
            Zero-based qubit indices the gate acts on.

        Returns
        -------
        Circuit
            New circuit containing the existing operations followed by the
            new gate operation.

        Raises
        ------
        TypeError
            If ``gate`` is not a Gate object.
        TypeError
            If ``qubits`` is not a tuple or contains non-integer entries.
        ValueError
            If any qubit index is negative, duplicated, or outside the circuit.
        ValueError
            If the number of qubit indices does not match the gate arity.
        """
        operation = Operation(gate=gate, qubits=qubits)
        return self.append(operation=operation)

    def extend(self, operations: tuple[Operation, ...]) -> Circuit:
        """Return a new circuit with multiple operations appended.

        Parameters
        ----------
        operations : tuple[Operation, ...]
            Operations to append to the circuit.

        Returns
        -------
        Circuit
            New circuit containing the existing operations followed by the
            appended operations in order.

        Raises
        ------
        TypeError
            If ``operations`` is not a tuple.
        TypeError
            If any entry is not an Operation object.
        ValueError
            If any operation uses a qubit index outside the circuit.
        """
        if not isinstance(operations, tuple):
            raise TypeError("operations must be a tuple.")

        new_circuit = self
        for operation in operations:
            new_circuit = new_circuit.append(operation=operation)

        return new_circuit

    def __len__(self) -> int:
        """Return the number of operations in the circuit.

        Returns
        -------
        int
            Number of operations stored in the circuit.
        """
        return len(self.operations)

    def __iter__(self) -> Iterator[Operation]:
        """Iterate over circuit operations in order.

        Returns
        -------
        Iterator[Operation]
            Iterator over the ordered operations in the circuit.
        """
        return iter(self.operations)

    def _validate_operation_qubits(self, operation: Operation) -> None:
        """Validate that an operation acts only on qubits in this circuit."""
        for qubit in operation.qubits:
            if qubit >= self.num_qubits:
                raise ValueError("operation qubit index is out of range.")
