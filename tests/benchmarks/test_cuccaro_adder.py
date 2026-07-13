from __future__ import annotations

import io

import pytest

from benchmarks.benchmark_cuccaro_adder import (
    REGISTER_WIDTHS,
    CuccaroAdderBenchmarkResult,
    benchmark_cuccaro_adder,
    build_benchmark_circuit,
    run_cuccaro_adder_benchmarks,
    write_benchmark_csv,
)


def test_register_widths_match_project_benchmark_sizes() -> None:
    """Use the fixed Cuccaro adder benchmark sizes from the roadmap."""
    assert REGISTER_WIDTHS == (2, 3, 4, 8, 16)


def test_build_benchmark_circuit_uses_expected_register_size() -> None:
    """Build a benchmark circuit with two n-bit registers and one work qubit."""
    circuit = build_benchmark_circuit(4)

    assert circuit.num_qubits == 9


def test_benchmark_cuccaro_adder_matches_expected_counts_for_special_case() -> None:
    """Report expected logical resources for the compact two-bit adder."""
    result = benchmark_cuccaro_adder(2)

    assert result == CuccaroAdderBenchmarkResult(
        num_bits=2,
        required_clean_work_qubits=1,
        logical_qubit_count=5,
        gate_count=3,
        t_count=0,
        expanded_t_count=7,
        cnot_count=2,
        toffoli_count=1,
        serial_depth=3,
        parallel_depth=2,
    )


def test_benchmark_cuccaro_adder_matches_expected_counts_for_general_case() -> None:
    """Report expected logical resources for a general Cuccaro adder."""
    result = benchmark_cuccaro_adder(4)

    assert result == CuccaroAdderBenchmarkResult(
        num_bits=4,
        required_clean_work_qubits=1,
        logical_qubit_count=9,
        gate_count=24,
        t_count=0,
        expanded_t_count=56,
        cnot_count=16,
        toffoli_count=8,
        serial_depth=24,
        parallel_depth=21,
    )


def test_run_cuccaro_adder_benchmarks_preserves_requested_order() -> None:
    """Return benchmark results in the same order as requested widths."""
    results = run_cuccaro_adder_benchmarks((4, 2, 3))

    assert tuple(result.num_bits for result in results) == (4, 2, 3)


def test_write_benchmark_csv_emits_expected_header_and_rows() -> None:
    """Write Cuccaro adder benchmark results in stable CSV column order."""
    output = io.StringIO()
    results = (
        CuccaroAdderBenchmarkResult(
            num_bits=2,
            required_clean_work_qubits=1,
            logical_qubit_count=5,
            gate_count=3,
            t_count=0,
            expanded_t_count=7,
            cnot_count=2,
            toffoli_count=1,
            serial_depth=3,
            parallel_depth=2,
        ),
    )

    write_benchmark_csv(results, output=output)

    assert output.getvalue() == (
        "num_bits,required_clean_work_qubits,logical_qubit_count,"
        "gate_count,t_count,expanded_t_count,cnot_count,toffoli_count,"
        "serial_depth,parallel_depth\r\n"
        "2,1,5,3,0,7,2,1,3,2\r\n"
    )


@pytest.mark.parametrize(
    "num_bits",
    [True, 1.5, "4"],
)
def test_build_benchmark_circuit_rejects_non_integer_widths(
    num_bits: object,
) -> None:
    """Reject non-integer benchmark register widths."""
    with pytest.raises(TypeError, match="num_bits must be an integer."):
        build_benchmark_circuit(num_bits)  # type: ignore[arg-type]


def test_build_benchmark_circuit_rejects_nonpositive_width() -> None:
    """Reject nonpositive benchmark register widths."""
    with pytest.raises(ValueError, match="num_bits must be positive."):
        build_benchmark_circuit(0)


def test_run_cuccaro_adder_benchmarks_rejects_non_tuple_widths() -> None:
    """Reject non-tuple benchmark width collections."""
    with pytest.raises(TypeError, match="register_widths must be a tuple."):
        run_cuccaro_adder_benchmarks([2, 3])  # type: ignore[arg-type]
