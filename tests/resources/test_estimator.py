import pytest

from qc_compiler.circuits import Circuit
from qc_compiler.gates import CNOT, CZ, T, X
from qc_compiler.resources import ResourceEstimator


TRIVIAL_CIRCUIT = Circuit(num_qubits=2)
NONTRIVIAL_CIRCUIT = (
    Circuit(num_qubits=2)
    .append_gate(gate=T, qubits=(0,))
    .append_gate(gate=CNOT, qubits=(0, 1))
    .append_gate(gate=CZ, qubits=(0, 1))
    .append_gate(gate=X, qubits=(1,))
)


def test_resource_estimator_estimates_empty_circuit():
    """Verify that an empty circuit produces zero resource counts."""
    estimate = ResourceEstimator().estimate(TRIVIAL_CIRCUIT)

    assert estimate.gate_count == 0
    assert estimate.t_count == 0
    assert estimate.cnot_count == 0
    assert estimate.cz_count == 0
    assert estimate.ancilla_count == 0
    assert estimate.depth is None


def test_resource_estimator_counts_total_gates():
    """Verify that the estimator counts total circuit operations."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.gate_count == 4


def test_resource_estimator_counts_t_gates():
    """Verify that the estimator counts T gates."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.t_count == 1


def test_resource_estimator_counts_cnot_gates():
    """Verify that the estimator counts controlled-NOT gates."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.cnot_count == 1


def test_resource_estimator_counts_cz_gates():
    """Verify that the estimator counts controlled-Z gates."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.cz_count == 1


def test_resource_estimator_sets_ancilla_count_to_zero():
    """Verify that the initial estimator assumes zero ancilla qubits."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.ancilla_count == 0


def test_resource_estimator_leaves_depth_unset():
    """Verify that depth is unset before a depth model is implemented."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.depth is None


def test_resource_estimator_rejects_non_circuit_input():
    """Verify that the estimator rejects non-Circuit inputs."""
    with pytest.raises(TypeError):
        ResourceEstimator().estimate("string")


def test_resource_estimator_imports_from_package():
    """Verify that ResourceEstimator is exposed through the public resources package."""
    from qc_compiler.resources import ResourceEstimator as ImportedResourceEstimator

    assert ImportedResourceEstimator is ResourceEstimator
