from dataclasses import FrozenInstanceError

import pytest

from qc_compiler.circuits import Operation
from qc_compiler.gates import Gate


X = Gate(name="X", arity=1)
CNOT = Gate(name="CNOT", arity=2)


def test_operation_constructs_valid_operation():
    """Verify that a valid operation stores its gate and qubits."""
    op = Operation(gate=X, qubits=(0,))

    assert op.gate == X
    assert op.qubits == (0,)


def test_operation_rejects_non_gate():
    """Verify that gate must be a Gate object."""
    with pytest.raises(TypeError):
        Operation(gate="X", qubits=(0,))


def test_operation_rejects_non_tuple_qubits():
    """Verify that qubits must be provided as a tuple."""
    with pytest.raises(TypeError):
        Operation(gate=X, qubits=[0])


def test_operation_rejects_wrong_number_of_qubits():
    """Verify that qubit count must match gate arity."""
    with pytest.raises(ValueError):
        Operation(gate=X, qubits=(0, 1))


def test_operation_rejects_duplicate_qubits():
    """Verify that duplicate qubit indices are rejected."""
    with pytest.raises(ValueError):
        Operation(gate=CNOT, qubits=(0, 0))


def test_operation_rejects_negative_qubits():
    """Verify that negative qubit indices are rejected."""
    with pytest.raises(ValueError):
        Operation(gate=X, qubits=(-1,))


def test_operation_rejects_non_integer_qubits():
    """Verify that non-integer qubit indices are rejected."""
    with pytest.raises(TypeError):
        Operation(gate=X, qubits=(1.5,))


def test_operation_is_immutable():
    """Verify that operation instances cannot be modified after construction."""
    op = Operation(gate=X, qubits=(0,))

    with pytest.raises(FrozenInstanceError):
        op.qubits = (1,)


def test_operation_imports_from_package():
    """Verify that Operation is exposed through the public circuits package."""
    from qc_compiler.circuits import Operation as ImportedOperation

    assert ImportedOperation is Operation
