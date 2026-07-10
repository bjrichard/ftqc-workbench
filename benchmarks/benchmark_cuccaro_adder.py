from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from typing import TextIO

from qc_compiler.circuits import Circuit
from qc_compiler.circuits.builders import build_cuccaro_adder
from qc_compiler.resources import ResourceEstimator


REGISTER_WIDTHS: tuple[int, ...] = (2, 3, 4, 8, 16)


@dataclass(frozen=True)
class CuccaroAdderBenchmarkResult:
    """Logical resource results for one Cuccaro adder circuit.

    Parameters
    ----------
    num_bits
        Number of bits in each input register.
    required_clean_work_qubits
        Number of clean carry/work qubits required by the implemented
        construction. This value is derived from the builder convention rather
        than from ``ResourceEstimate.ancilla_count``.
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
    ``required_clean_work_qubits`` and the estimator's ``ancilla_count``
    represent different quantities. The current circuit Intermediate
    Representation (IR) does not retain qubit-role metadata, so the estimator
    reports an ancilla count of zero. This benchmark records the
    construction-level clean-carry requirement explicitly.
    """

    num_bits: int
    required_clean_work_qubits: int
    logical_qubit_count: int
    gate_count: int
    t_count: int
    cnot_count: int
    toffoli_count: int
    serial_depth: int
    parallel_depth: int


def build_benchmark_circuit(num_bits: int) -> Circuit:
    """Construct a Cuccaro adder circuit for benchmarking.

    Parameters
    ----------
    num_bits
        Number of bits in each input register. At least one bit is required.

    Returns
    -------
    Circuit
        Cuccaro-style in-place modular adder using a deterministic register
        layout. The preserved addend register ``a`` occupies indices ``0``
        through ``num_bits - 1``, the overwritten addend register ``b``
        occupies indices ``num_bits`` through ``2 * num_bits - 1``, and the
        clean carry qubit occupies index ``2 * num_bits``.

    Raises
    ------
    TypeError
        If ``num_bits`` is not an integer or is a Boolean.
    ValueError
        If ``num_bits`` is less than one.

    Notes
    -----
    The register layout is:

    - ``a``: ``(0, 1, ..., num_bits - 1)``
    - ``b``: ``(num_bits, num_bits + 1, ..., 2 * num_bits - 1)``
    - clean carry: ``2 * num_bits``

    The total register size is ``2 * num_bits + 1``.

    This function does not reproduce the synthesis algorithm. It assigns
    benchmark qubit indices and delegates circuit construction to
    ``build_cuccaro_adder``.
    """
    if isinstance(num_bits, bool) or not isinstance(num_bits, int):
        raise TypeError("num_bits must be an integer.")

    if num_bits < 1:
        raise ValueError("num_bits must be positive.")

    a = tuple(range(num_bits))
    b = tuple(range(num_bits, 2 * num_bits))
    carry = 2 * num_bits
    num_qubits = 2 * num_bits + 1

    return build_cuccaro_adder(
        a=a,
        b=b,
        carry=carry,
        num_qubits=num_qubits,
    )


def benchmark_cuccaro_adder(
    num_bits: int,
) -> CuccaroAdderBenchmarkResult:
    """Benchmark logical resources for one Cuccaro adder circuit.

    Parameters
    ----------
    num_bits
        Number of bits in each input register.

    Returns
    -------
    CuccaroAdderBenchmarkResult
        Logical resource counts and construction-level clean-carry
        requirements for the generated circuit.

    Raises
    ------
    TypeError
        If ``num_bits`` is not an integer or is a Boolean.
    ValueError
        If ``num_bits`` is less than one.
    RuntimeError
        If the resource estimator does not provide serial or parallel depth.

    Notes
    -----
    The circuit is constructed by ``build_benchmark_circuit`` and analyzed
    using the current ``ResourceEstimator``.

    The clean-carry requirement is computed from the adder construction
    convention because the current circuit Intermediate Representation (IR)
    does not retain ancilla-role metadata.
    """
    circuit = build_benchmark_circuit(num_bits)
    estimate = ResourceEstimator().estimate(circuit)

    if estimate.depth is None or estimate.parallel_depth is None:
        raise RuntimeError("Benchmark requires depth estimates.")

    return CuccaroAdderBenchmarkResult(
        num_bits=num_bits,
        required_clean_work_qubits=1,
        logical_qubit_count=estimate.logical_qubit_count,
        gate_count=estimate.gate_count,
        t_count=estimate.t_count,
        cnot_count=estimate.cnot_count,
        toffoli_count=estimate.toffoli_count,
        serial_depth=estimate.depth,
        parallel_depth=estimate.parallel_depth,
    )


def run_cuccaro_adder_benchmarks(
    register_widths: tuple[int, ...] = REGISTER_WIDTHS,
) -> tuple[CuccaroAdderBenchmarkResult, ...]:
    """Run Cuccaro adder resource benchmarks.

    Parameters
    ----------
    register_widths
        Ordered tuple of register widths to benchmark. Each width is the
        number of bits in each input register and must be a valid positive
        integer accepted by ``benchmark_cuccaro_adder``.

    Returns
    -------
    tuple[CuccaroAdderBenchmarkResult, ...]
        Benchmark results in the same order as ``register_widths``.

    Raises
    ------
    TypeError
        If ``register_widths`` is not a tuple.
    TypeError
        If any register width is not an integer or is a Boolean.
    ValueError
        If any register width is less than one.

    Notes
    -----
    This function performs logical resource analysis only. It does not measure
    wall-clock runtime, memory consumption, physical qubit requirements, or
    fault-tolerant execution cost.

    Each result is generated independently using the current
    ``ResourceEstimator`` and the Cuccaro adder builder.
    """
    if not isinstance(register_widths, tuple):
        raise TypeError("register_widths must be a tuple.")

    return tuple(
        benchmark_cuccaro_adder(num_bits)
        for num_bits in register_widths
    )


def write_benchmark_csv(
    results: tuple[CuccaroAdderBenchmarkResult, ...],
    output: TextIO | None = None,
) -> None:
    """Write Cuccaro adder benchmark results as CSV.

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
            "num_bits",
            "required_clean_work_qubits",
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
                result.num_bits,
                result.required_clean_work_qubits,
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
    results = run_cuccaro_adder_benchmarks()
    write_benchmark_csv(results)


if __name__ == "__main__":
    main()
