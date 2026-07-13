import pytest

from benchmarks.benchmark_multi_controlled_x import (
    CONTROL_COUNTS,
    benchmark_multi_controlled_x,
    build_benchmark_circuit,
    run_multi_controlled_x_benchmarks,
)


@pytest.mark.parametrize("num_controls", CONTROL_COUNTS)
def test_benchmark_circuit_uses_expected_register_size(
    num_controls: int,
) -> None:
    """Use the expected number of controls, target, and clean ancillas."""
    circuit = build_benchmark_circuit(num_controls)

    assert circuit.num_qubits == 2 * num_controls - 1


@pytest.mark.parametrize("num_controls", CONTROL_COUNTS)
def test_benchmark_matches_expected_resource_scaling(
    num_controls: int,
) -> None:
    """Match the clean-ancilla ladder's analytical resource formulas."""
    result = benchmark_multi_controlled_x(num_controls)

    expected_toffoli_count = 2 * num_controls - 3

    assert result.required_clean_ancillas == num_controls - 2
    assert result.logical_qubit_count == 2 * num_controls - 1
    assert result.gate_count == expected_toffoli_count
    assert result.toffoli_count == expected_toffoli_count
    assert result.t_count == 0
    assert result.expanded_t_count == 7 * expected_toffoli_count
    assert result.cnot_count == 0
    assert result.serial_depth == expected_toffoli_count
    assert result.parallel_depth == expected_toffoli_count
    

def test_run_benchmarks_preserves_control_count_order() -> None:
    """Return benchmark rows in the configured order."""
    results = run_multi_controlled_x_benchmarks()

    assert tuple(result.num_controls for result in results) == CONTROL_COUNTS
