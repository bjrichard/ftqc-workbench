# Multi-controlled Pauli-X benchmark

## Purpose

This benchmark records logical resource estimates for the implemented
clean-ancilla multi-controlled Pauli-X construction.

It benchmarks the fixed control counts defined in the project roadmap:

- 2
- 3
- 4
- 5
- 8
- 16

The benchmark measures logical circuit structure. It does not measure
wall-clock runtime, physical qubits, routing overhead, error-correction cost,
or hardware execution time.

## Reproduction

Run from the repository root:

```bash
python benchmarks/benchmark_multi_controlled_x.py
