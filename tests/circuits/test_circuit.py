from dataclasses import FrozenInstanceError

import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, X


X_0 = Operation(gate=X, qubits=(0,))
CNOT_0_1 = Operation(gate=CNOT, qubits=(0, 1))


def test_circuit_constructs_valid_empty_circuit():
    """Verify that a valid empty circuit stores its qubit count and operations."""
    circuit = Circuit(num_qubits=2)

    assert circuit.num_qubits == 2
    assert circuit.operations == ()


def test_circuit_rejects_non_integer_num_qubits():
    """Verify that circuit qubit count must be an integer."""
    with pytest.raises(TypeError):
        Circuit(num_qubits=2.5, operations=(CNOT_0_1,))


def test_circuit_rejects_zero_num_qubits():
    """Verify that zero-qubit circuits are rejected."""
    with pytest.raises(ValueError):
        Circuit(num_qubits=0)


def test_circuit_rejects_negative_num_qubits():
    """Verify that negative circuit qubit counts are rejected."""
    with pytest.raises(ValueError):
        Circuit(num_qubits=-1)


def test_circuit_rejects_non_tuple_operations():
    """Verify that circuit operations must be provided as a tuple."""
    with pytest.raises(TypeError):
        Circuit(num_qubits=2, operations=X_0)


def test_circuit_rejects_non_operation_entries():
    """Verify that circuit operations must contain only Operation objects."""
    with pytest.raises(TypeError):
        Circuit(num_qubits=2, operations=(1, 2, 3))


def test_circuit_append_returns_new_circuit():
    """Verify that append returns a new circuit containing the added operation."""
    circuit = Circuit(num_qubits=2)
    new_circuit = circuit.append(operation=X_0)

    assert new_circuit is not circuit
    assert new_circuit.operations == (X_0,)


def test_circuit_append_preserves_original_circuit():
    """Verify that append does not mutate the original circuit."""
    circuit = Circuit(num_qubits=2)
    circuit.append(operation=X_0)

    assert circuit.num_qubits == 2
    assert circuit.operations == ()


def test_circuit_append_gate_returns_new_circuit():
    """Verify that append_gate returns a new circuit containing the added gate."""
    circuit = Circuit(num_qubits=2)
    new_circuit = circuit.append_gate(gate=X, qubits=(0,))

    assert new_circuit is not circuit
    assert new_circuit.operations == (Operation(gate=X, qubits=(0,)),)


def test_circuit_append_gate_preserves_original_circuit():
    """Verify that append_gate does not mutate the original circuit."""
    circuit = Circuit(num_qubits=2)
    circuit.append_gate(gate=X, qubits=(0,))

    assert circuit.num_qubits == 2
    assert circuit.operations == ()


def test_circuit_append_gate_rejects_out_of_range_qubits():
    """Verify that append_gate rejects qubits outside the circuit."""
    circuit = Circuit(num_qubits=2)

    with pytest.raises(ValueError):
        circuit.append_gate(gate=X, qubits=(2,))


def test_circuit_append_gate_rejects_non_tuple_qubits():
    """Verify that append_gate rejects non-tuple qubit inputs."""
    circuit = Circuit(num_qubits=2)

    with pytest.raises(TypeError):
        circuit.append_gate(gate=X, qubits=[0])


def test_circuit_append_gate_rejects_non_gate_input():
    """Verify that append_gate rejects inputs that cannot form an operation."""
    circuit = Circuit(num_qubits=2)

    with pytest.raises(TypeError):
        circuit.append_gate(gate="X", qubits=(0,))


def test_circuit_extend_returns_new_circuit():
    """Verify that extend returns a new circuit containing the added operations."""
    circuit = Circuit(num_qubits=2)
    new_circuit = circuit.extend((X_0, CNOT_0_1, X_0))

    assert new_circuit is not circuit
    assert new_circuit.operations == (X_0, CNOT_0_1, X_0)


def test_circuit_extend_preserves_original_circuit():
    """Verify that extend does not mutate the original circuit."""
    circuit = Circuit(num_qubits=2)
    circuit.extend((X_0, CNOT_0_1, X_0))

    assert circuit.num_qubits == 2
    assert circuit.operations == ()


def test_circuit_extend_preserves_operation_order():
    """Verify that extend preserves the order of appended operations."""
    circuit = Circuit(num_qubits=2)
    new_circuit = circuit.extend((X_0, CNOT_0_1, X_0))

    assert new_circuit.operations == (X_0, CNOT_0_1, X_0)


def test_circuit_extend_rejects_non_tuple_operations():
    """Verify that extend rejects non-tuple operation inputs."""
    circuit = Circuit(num_qubits=2)

    with pytest.raises(TypeError):
        circuit.extend([X_0, CNOT_0_1, X_0])


def test_circuit_extend_rejects_non_operation_entries():
    """Verify that extend rejects entries that are not Operation objects."""
    circuit = Circuit(num_qubits=2)

    with pytest.raises(TypeError):
        circuit.extend(("X_0", CNOT_0_1, X_0))


def test_circuit_extend_rejects_out_of_range_operation_qubits():
    """Verify that extend rejects operations using qubits outside the circuit."""
    circuit = Circuit(num_qubits=1)

    with pytest.raises(ValueError):
        circuit.extend((CNOT_0_1,))


def test_circuit_rejects_out_of_range_operation_qubits():
    """Verify that operations cannot use qubit indices outside the circuit."""
    X_3 = Operation(gate=X, qubits=(3,))

    with pytest.raises(ValueError):
        Circuit(num_qubits=2, operations=(X_3,))


def test_circuit_supports_len():
    """Verify that len(circuit) returns the number of operations."""
    circuit = Circuit(num_qubits=2, operations=(X_0, CNOT_0_1))

    assert len(circuit) == 2


def test_circuit_supports_iteration():
    """Verify that circuits can be iterated over operation-by-operation."""
    circuit = Circuit(num_qubits=2, operations=(X_0, CNOT_0_1))

    assert list(circuit) == [X_0, CNOT_0_1]


def test_circuit_is_immutable():
    """Verify that circuit instances cannot be modified after construction."""
    circuit = Circuit(num_qubits=2, operations=(X_0, CNOT_0_1))

    with pytest.raises(FrozenInstanceError):
        circuit.num_qubits = 3


def test_circuit_imports_from_package():
    """Verify that Circuit is exposed through the public circuits package."""
    from qc_compiler.circuits import Circuit as ImportedCircuit

    assert ImportedCircuit is Circuit
