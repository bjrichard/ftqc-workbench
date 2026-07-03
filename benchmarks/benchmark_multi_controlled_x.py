from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from typing import TextIO

from qc_compiler.circuits import Circuit
from qc_compiler.circuits.builders import build_multi_controlled_x
from qc_compiler.resources import ResourceEstimator


CONTROL_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 8, 16)


@dataclass(frozen=True)
class MultiControlledXBenchmarkResult:
    """Logical resource results for one multi-controlled Pauli-X circuit.

    Parameters
    ----------
    num_controls
        Number of control qubits in the benchmarked circuit.
    required_clean_ancillas
        Number of clean ancillas required by the implemented construction.
        This value is derived from the builder convention rather than from
        ``ResourceEstimate.ancilla_count``.
    logical_qubit_count
        Total number of logical qubit slots in the generated circuit.
    gate_count
        Total number of logical operations in the circuit.
    t_count
        Number of primitive T gates in the circuit.
    cnot_count
        Number of primitive Controlled-NOT (CNOT) gates in the circuit.
    toffoli_count
        Number of primitive Toffoli gates in the circuit.
    serial_depth
        Serial circuit depth reported by the current resource model.
    parallel_depth
        Dependency-preserving parallel depth reported by the resource
        estimator.

    Notes
    -----
    ``required_clean_ancillas`` and the estimator's ``ancilla_count`` represent
    different quantities. The current circuit Intermediate Representation
    (IR) does not retain qubit-role metadata, so the estimator reports an
    ancilla count of zero. This benchmark records the construction-level
    clean-ancilla requirement explicitly.
    """

    num_controls: int
    required_clean_ancillas: int
    logical_qubit_count: int
    gate_count: int
    t_count: int
    cnot_count: int
    toffoli_count: int
    serial_depth: int
    parallel_depth: int


def build_benchmark_circuit(num_controls: int) -> Circuit:
    """Construct a multi-controlled Pauli-X circuit for benchmarking.

    Parameters
    ----------
    num_controls
        Number of control qubits in the benchmark circuit. At least one
        control qubit is required.

    Returns
    -------
    Circuit
        Multi-controlled Pauli-X circuit using a deterministic register
        layout. Controls occupy indices ``0`` through ``num_controls - 1``,
        the target occupies index ``num_controls``, and any required clean
        ancillas occupy consecutive higher indices.

    Raises
    ------
    TypeError
        If ``num_controls`` is not an integer or is a Boolean.
    ValueError
        If ``num_controls`` is less than one.

    Notes
    -----
    For one or two controls, no clean ancillas are required. For three or more
    controls, the implemented construction requires exactly
    ``num_controls - 2`` clean ancillas.

    The register layout is:

    - controls: ``(0, 1, ..., num_controls - 1)``
    - target: ``num_controls``
    - clean ancillas: consecutive indices beginning at
      ``num_controls + 1``

    The total register size is

    ``num_controls + 1 + max(0, num_controls - 2)``.

    For the configured benchmark sizes, where ``num_controls >= 2``, this
    simplifies to ``2 * num_controls - 1``.

    This function does not reproduce the synthesis algorithm. It assigns
    benchmark qubit indices and delegates circuit construction to
    ``build_multi_controlled_x``.
    """
    if isinstance(num_controls, bool) or not isinstance(num_controls, int):
        raise TypeError("num_controls must be an integer.")

    if num_controls < 1:
        raise ValueError("num_controls must be positive.")

    controls = tuple(range(num_controls))
    target = num_controls
    required_clean_ancillas = max(0, num_controls - 2)
    ancillas = tuple(
        range(
            num_controls + 1,
            num_controls + 1 + required_clean_ancillas,
        )
    )
    num_qubits = num_controls + 1 + required_clean_ancillas

    return build_multi_controlled_x(
        controls=controls,
        target=target,
        ancillas=ancillas,
        num_qubits=num_qubits,
    )


def benchmark_multi_controlled_x(
    num_controls: int,
) -> MultiControlledXBenchmarkResult:
    """Benchmark logical resources for one multi-controlled Pauli-X circuit.

    Parameters
    ----------
    num_controls
        Number of control qubits in the generated benchmark circuit.

    Returns
    -------
    MultiControlledXBenchmarkResult
        Logical resource counts and construction-level clean-ancilla
        requirements for the generated circuit.

    Raises
    ------
    TypeError
        If ``num_controls`` is not an integer or is a Boolean.
    ValueError
        If ``num_controls`` is less than one.
    RuntimeError
        If the resource estimator does not provide serial or parallel depth.

    Notes
    -----
    The circuit is constructed by ``build_benchmark_circuit`` and analyzed
    using the current ``ResourceEstimator``.

    The clean-ancilla requirement is computed from the multi-controlled
    Pauli-X construction convention because the current circuit Intermediate
    Representation (IR) does not retain ancilla-role metadata.
    """
    circuit = build_benchmark_circuit(num_controls)
    estimate = ResourceEstimator().estimate(circuit)

    if estimate.depth is None or estimate.parallel_depth is None:
        raise RuntimeError("Benchmark requires depth estimates.")

    return MultiControlledXBenchmarkResult(
        num_controls=num_controls,
        required_clean_ancillas=max(0, num_controls - 2),
        logical_qubit_count=estimate.logical_qubit_count,
        gate_count=estimate.gate_count,
        t_count=estimate.t_count,
        cnot_count=estimate.cnot_count,
        toffoli_count=estimate.toffoli_count,
        serial_depth=estimate.depth,
        parallel_depth=estimate.parallel_depth,
    )


def run_multi_controlled_x_benchmarks(
    control_counts: tuple[int, ...] = CONTROL_COUNTS,
) -> tuple[MultiControlledXBenchmarkResult, ...]:
    """Run multi-controlled Pauli-X resource benchmarks.

    Parameters
    ----------
    control_counts
        Ordered tuple of control counts to benchmark. Each value must be a
        valid positive integer accepted by ``benchmark_multi_controlled_x``.

    Returns
    -------
    tuple[MultiControlledXBenchmarkResult, ...]
        Benchmark results in the same order as ``control_counts``.

    Raises
    ------
    TypeError
        If ``control_counts`` is not a tuple.
    TypeError
        If any control count is not an integer or is a Boolean.
    ValueError
        If any control count is less than one.

    Notes
    -----
    This function performs logical resource analysis only. It does not measure
    wall-clock runtime, memory consumption, physical qubit requirements, or
    fault-tolerant execution cost.

    Each result is generated independently using the current
    ``ResourceEstimator`` and the clean-ancilla multi-controlled Pauli-X
    builder.
    """
    if not isinstance(control_counts, tuple):
        raise TypeError("control_counts must be a tuple.")

    return tuple(
        benchmark_multi_controlled_x(num_controls)
        for num_controls in control_counts
    )


def write_benchmark_csv(
    results: tuple[MultiControlledXBenchmarkResult, ...],
    output: TextIO | None = None,
) -> None:
    """Write multi-controlled Pauli-X benchmark results as CSV.

    Parameters
    ----------
    results
        Ordered benchmark results to serialize.
    output
        Text stream receiving the CSV output. If omitted, output is written
        to standard output.

    Returns
    -------
    None
        The function writes rows to ``output`` and returns no value.

    Notes
    -----
    The column order is stable so benchmark output can be redirected to a file
    and consumed by documentation or later analysis scripts.

    Standard output is resolved when the function is called rather than when
    the module is imported. This preserves compatibility with output
    redirection and test-capture mechanisms.
    """
    if output is None:
        output = sys.stdout

    writer = csv.writer(output)

    writer.writerow(
        (
            "num_controls",
            "required_clean_ancillas",
            "logical_qubit_count",
            "gate_count",
            "t_count",
            "cnot_count",
            "toffoli_count",
            "serial_depth",
            "parallel_depth",
        )
    )

    for result in results:
        writer.writerow(
            (
                result.num_controls,
                result.required_clean_ancillas,
                result.logical_qubit_count,
                result.gate_count,
                result.t_count,
                result.cnot_count,
                result.toffoli_count,
                result.serial_depth,
                result.parallel_depth,
            )
        )


def main() -> None:
    """Run the default benchmark suite and write CSV results."""
    results = run_multi_controlled_x_benchmarks()
    write_benchmark_csv(results)


if __name__ == "__main__":
    main()
