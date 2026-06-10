import pytest

from qc_compiler.circuits import Circuit
from qc_compiler.gates import CNOT, X, Z
from qc_compiler.resources import estimate_parallel_depth


def test_parallel_depth_of_empty_circuit_is_zero():
    """Verify that an empty circuit has parallelized depth zero."""
    circuit = Circuit(num_qubits=2)

    assert estimate_parallel_depth(circuit) == 0


def test_parallel_depth_counts_single_operation_as_one_layer():
    """Verify that one operation has parallelized depth one."""
    circuit = Circuit(num_qubits=1).append_gate(gate=X, qubits=(0,))

    assert estimate_parallel_depth(circuit) == 1


def test_parallel_depth_combines_disjoint_single_qubit_operations():
    """Verify that disjoint operations can share one layer."""
    circuit = (
        Circuit(num_qubits=2)
        .append_gate(gate=X, qubits=(0,))
        .append_gate(gate=Z, qubits=(1,))
    )

    assert estimate_parallel_depth(circuit) == 1


def test_parallel_depth_separates_operations_on_same_qubit():
    """Verify that operations sharing a qubit require separate layers."""
    circuit = (
        Circuit(num_qubits=1)
        .append_gate(gate=X, qubits=(0,))
        .append_gate(gate=Z, qubits=(0,))
    )

    assert estimate_parallel_depth(circuit) == 2


def test_parallel_depth_handles_two_qubit_gate_conflicts():
    """Verify that a two-qubit gate conflicts with operations on either qubit."""
    circuit = (
        Circuit(num_qubits=2)
        .append_gate(gate=X, qubits=(0,))
        .append_gate(gate=Z, qubits=(1,))
        .append_gate(gate=CNOT, qubits=(0, 1))
    )

    assert estimate_parallel_depth(circuit) == 2


def test_parallel_depth_can_reuse_later_available_layers():
    """Verify that operations are placed in the earliest compatible layer."""
    circuit = (
        Circuit(num_qubits=3)
        .append_gate(gate=CNOT, qubits=(0, 1))
        .append_gate(gate=X, qubits=(0,))
        .append_gate(gate=Z, qubits=(2,))
    )

    assert estimate_parallel_depth(circuit) == 2


def test_parallel_depth_rejects_non_circuit_input():
    """Verify that parallelized depth estimation rejects non-Circuit inputs."""
    with pytest.raises(TypeError):
        estimate_parallel_depth("not a circuit")


def test_parallel_depth_imports_from_package():
    """Verify that estimate_parallel_depth is exposed through the resources package."""
    from qc_compiler.resources import (
        estimate_parallel_depth as imported_estimate_parallel_depth,
    )

    assert imported_estimate_parallel_depth is estimate_parallel_depth
