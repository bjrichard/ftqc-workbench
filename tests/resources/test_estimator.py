import pytest

from qc_compiler.circuits import Circuit, build_multi_controlled_x
from qc_compiler.gates import CNOT, CZ, T, TOFFOLI, X, Z
from qc_compiler.resources import ResourceEstimator


TRIVIAL_CIRCUIT = Circuit(num_qubits=2)
NONTRIVIAL_CIRCUIT = (
    Circuit(num_qubits=2)
    .append_gate(gate=T, qubits=(0,))
    .append_gate(gate=CNOT, qubits=(0, 1))
    .append_gate(gate=CZ, qubits=(0, 1))
    .append_gate(gate=X, qubits=(1,))
)
PARALLELIZABLE_CIRCUIT = (
    Circuit(num_qubits=2)
    .append_gate(gate=X, qubits=(0,))
    .append_gate(gate=Z, qubits=(1,))
    .append_gate(gate=CNOT, qubits=(0, 1))
)
TOFFOLI_CIRCUIT = Circuit(num_qubits=3).append_gate(
    gate=TOFFOLI,
    qubits=(0, 1, 2),
)
MULTI_CONTROLLED_X_CIRCUIT = build_multi_controlled_x(
    controls=(0, 1, 2, 3),
    target=4,
    ancillas=(5, 6),
    num_qubits=7,
)


def test_resource_estimator_estimates_empty_circuit():
    """Verify that an empty circuit produces zero resource counts."""
    estimate = ResourceEstimator().estimate(TRIVIAL_CIRCUIT)

    assert estimate.gate_count == 0
    assert estimate.t_count == 0
    assert estimate.cnot_count == 0
    assert estimate.cz_count == 0
    assert estimate.toffoli_count == 0
    assert estimate.logical_qubit_count == 2
    assert estimate.ancilla_count == 0
    assert estimate.depth == 0
    assert estimate.parallel_depth == 0


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


def test_resource_estimator_counts_toffoli_gates():
    """Verify that the estimator counts Toffoli gates."""
    estimate = ResourceEstimator().estimate(TOFFOLI_CIRCUIT)

    assert estimate.toffoli_count == 1


def test_resource_estimator_counts_logical_qubits():
    """Verify that logical qubit count equals the circuit width."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.logical_qubit_count == 2


def test_resource_estimator_sets_ancilla_count_to_zero():
    """Verify that the initial estimator assumes zero ancilla qubits."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.ancilla_count == 0


def test_resource_estimator_estimates_empty_circuit_depth():
    """Verify that an empty circuit has serial depth zero."""
    estimate = ResourceEstimator().estimate(TRIVIAL_CIRCUIT)

    assert estimate.depth == 0


def test_resource_estimator_estimates_nonempty_circuit_serial_depth():
    """Verify that serial depth equals the number of operations."""
    estimate = ResourceEstimator().estimate(NONTRIVIAL_CIRCUIT)

    assert estimate.depth == 4


def test_resource_estimator_estimates_empty_circuit_parallel_depth():
    """Verify that an empty circuit has parallelized depth zero."""
    estimate = ResourceEstimator().estimate(TRIVIAL_CIRCUIT)

    assert estimate.parallel_depth == 0


def test_resource_estimator_estimates_parallel_depth():
    """Verify that the estimator reports greedy parallelized depth."""
    estimate = ResourceEstimator().estimate(PARALLELIZABLE_CIRCUIT)

    assert estimate.depth == 3
    assert estimate.parallel_depth == 2


def test_resource_estimator_counts_multi_controlled_x_resources():
    """Verify logical resource counts for a multi-controlled X ladder."""
    estimate = ResourceEstimator().estimate(MULTI_CONTROLLED_X_CIRCUIT)

    assert estimate.gate_count == 5
    assert estimate.t_count == 0
    assert estimate.cnot_count == 0
    assert estimate.cz_count == 0
    assert estimate.toffoli_count == 5
    assert estimate.logical_qubit_count == 7
    assert estimate.ancilla_count == 0
    assert estimate.depth == 5


def test_resource_estimator_rejects_non_circuit_input():
    """Verify that the estimator rejects non-Circuit inputs."""
    with pytest.raises(TypeError):
        ResourceEstimator().estimate("string")


def test_resource_estimator_imports_from_package():
    """Verify that ResourceEstimator is exposed through the public resources package."""
    from qc_compiler.resources import ResourceEstimator as ImportedResourceEstimator

    assert ImportedResourceEstimator is ResourceEstimator


def test_resource_estimator_preserves_multi_controlled_x_dependencies():
    """Preserve causal dependencies in a multi-controlled X ladder."""
    estimate = ResourceEstimator().estimate(MULTI_CONTROLLED_X_CIRCUIT)

    assert estimate.parallel_depth == 5
