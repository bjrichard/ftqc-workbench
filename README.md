# FTQC Workbench

`ftqc-workbench` is a compact Python workbench for building, simulating, verifying, and estimating logical resources for small fault-tolerant quantum computing (FTQC) circuit primitives.

The project focuses on the software layer between abstract quantum gates and early logical resource estimation. It provides:

- a minimal immutable circuit intermediate representation
- exact simulation and verification tools
- reversible primitive builders
- logical resource estimators
- Toffoli-expanded analytical T-count estimates
- readout-error mitigation utilities
- reproducible benchmarks and tests

The workbench does not model physical hardware, surface-code layouts, magic-state factories, routing, or runtime. Its purpose is to make logical circuit structure, workspace assumptions, and first-order resource conventions explicit and inspectable. The emphasis is on explicit conventions, testable abstractions, and reproducible resource tables rather than broad quantum software development kit (SDK) coverage.

## Why this project exists

High-level quantum algorithms are not limited by abstract gate count alone. Practical fault-tolerant implementations depend strongly on lower-level resources, especially non-Clifford operations such as T gates.

This project separates three layers:

- **Primitive logical estimates:** count the gates emitted by the circuit builders.
- **Expanded analytical estimates:** assign Toffoli gates an explicit T-count convention.
- **Physical resource estimates:** remain out of scope until lower-level assumptions are specified.

That separation is the main design principle of the workbench.

## Implemented modules

```text
src/qc_compiler/
├── circuits/      # circuit IR and reversible primitive builders
├── gates/         # primitive logical gate definitions
├── resources/     # logical resource estimation and expanded T-counts
├── simulation/    # exact simulation and equivalence support
├── mitigation/    # classical readout-error mitigation
└── compilation/   # early compiler-pass scaffolding

benchmarks/        # reproducible benchmark scripts
docs/              # design notes, resource-model notes, and benchmark results
tests/             # unit, verification, and benchmark tests
```

## Core circuit model

The workbench uses a minimal circuit intermediate representation:

- `Gate`: reusable logical gate definition
- `Operation`: a gate applied to concrete qubit indices
- `Circuit`: immutable ordered sequence of operations over a fixed qubit register

Qubits are represented by zero-based integer indices.

```python
from qc_compiler.circuits import Circuit
from qc_compiler.gates import H, CNOT

circuit = (
    Circuit(num_qubits=2)
    .append_gate(gate=H, qubits=(0,))
    .append_gate(gate=CNOT, qubits=(0, 1))
)
```

Appending an operation returns a new circuit rather than mutating the original.

## Implemented circuit primitives

### Multi-controlled Pauli-X

The workbench implements a clean-ancilla multi-controlled Pauli-X builder:

```python
from qc_compiler.circuits import build_multi_controlled_x

circuit = build_multi_controlled_x(
    controls=(0, 1, 2, 3),
    target=4,
    ancillas=(5, 6),
    num_qubits=7,
)
```

Implemented cases include:

- one control: `CNOT`
- two controls: `TOFFOLI`
- three or more controls: clean-ancilla Toffoli ladder

### Cuccaro-style modular adder

The workbench also implements an in-place Cuccaro-style modular adder:

```python
from qc_compiler.circuits import build_cuccaro_adder

circuit = build_cuccaro_adder(
    a=(0, 1, 2, 3),
    b=(4, 5, 6, 7),
    carry=8,
    num_qubits=9,
)
```

The builder preserves register `a`, writes the modular sum into register `b`, and restores the clean work qubit to `|0>`.

See [`docs/technical_details.md`](docs/technical_details.md) for formulas, register conventions, and scaling behavior.

## Simulation and verification

The project includes:

- exact statevector simulation
- basis-state reversible simulation
- unitary construction
- circuit equivalence checks up to global phase
- exhaustive truth-table tests for small reversible circuits
- deterministic randomized verification for larger primitives

The simulation layer is intended for correctness checks, not performance-scale quantum simulation.

## Resource estimation

The primitive `ResourceEstimator` reports logical bookkeeping metrics directly from the circuit intermediate representation:

- total gate count
- explicit primitive T-gate count
- Controlled-NOT (CNOT) count
- Controlled-Z (CZ) count
- Toffoli count
- logical qubit count
- serial depth
- dependency-preserving parallel depth

The workbench also supports an analytical Toffoli-expanded T-count estimate using the current convention:

```text
1 Toffoli = 7 T gates
```

This estimate does not decompose or mutate the circuit. It is a first-order accounting convention, not a physical resource estimate or T-depth model.

See [`docs/technical_details.md`](docs/technical_details.md) for the full resource model, formulas, assumptions, and limitations.

## Readout-error mitigation

The workbench includes classical readout-error mitigation utilities for measured bitstring counts.

Implemented mitigation support includes:

- single-qubit readout mitigation
- tensor-product multi-qubit mitigation for independent per-qubit assignment matrices
- explicit bitstring ordering
- linear inversion using known assignment matrices
- clipping and renormalization of mitigated probabilities

For tensor-product mitigation, bitstrings use display order `"q_{n-1}...q_1q_0"`, where the rightmost bit is qubit 0 and the least-significant bit.

Example:

```python
import numpy as np

from qc_compiler.mitigation import mitigate_single_qubit_readout


assignment_matrix = np.array(
    [
        [0.9, 0.1],
        [0.1, 0.9],
    ],
    dtype=float,
)

mitigated = mitigate_single_qubit_readout(
    counts={"0": 820, "1": 180},
    assignment_matrix=assignment_matrix,
)
```

This is post-processing of classical measurement results. It does not model gate noise, decoherence, calibration fitting, or hardware execution.

See [`docs/readout_mitigation_example.md`](docs/readout_mitigation_example.md) for a worked example.

## Benchmarks

Benchmark scripts are included for the implemented primitive families:

```bash
python benchmarks/benchmark_multi_controlled_x.py
python benchmarks/benchmark_cuccaro_adder.py
```

Saved benchmark documentation and comma-separated values (CSV) outputs are stored in:

```text
docs/benchmarks/
```

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/bjrichard/ftqc-workbench.git
cd ftqc-workbench
```

### 2. Create and activate an environment

Using conda:

```bash
conda create -n ftqc-workbench python=3.12
conda activate ftqc-workbench
```

Or use any Python 3.12-compatible virtual environment.

### 3. Install the package and development dependencies

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode along with the development tools used by the validation commands, including `pytest`, `ruff`, and `mypy`.

### 4. Run validation

```bash
pytest -q
ruff check .
```

### 5. Run benchmarks

```bash
python benchmarks/benchmark_multi_controlled_x.py
python benchmarks/benchmark_cuccaro_adder.py
```

## Repository guide

| Path | Purpose |
|---|---|
| `src/qc_compiler/circuits/` | Circuit IR and primitive builders |
| `src/qc_compiler/gates/` | Primitive gate definitions |
| `src/qc_compiler/resources/` | Resource estimation and expanded T-counts |
| `src/qc_compiler/simulation/` | Exact simulation and verification support |
| `src/qc_compiler/mitigation/` | Classical readout-error mitigation |
| `benchmarks/` | Reproducible benchmark scripts |
| `tests/` | Unit, verification, and benchmark tests |
| `docs/resource_model.md` | Current resource-model assumptions |
| `docs/simulation_conventions.md` | Simulation indexing and conventions |
| `docs/technical_details.md` | Detailed formulas, limitations, and future directions |
| `docs/readout_mitigation_example.md` | Readout mitigation example and limitations |
| `docs/benchmarks/` | Benchmark results and interpretation |

## Current limitations

The workbench is a logical circuit and resource-accounting project, not a production compiler or physical resource estimator.

It currently does not model:

- physical qubits or error-correction codes
- magic-state factories or distillation
- routing, topology, or hardware scheduling
- gate-level noise, decoherence, or calibration fitting
- correlated readout-error models
- T-depth or explicit Clifford+T decomposition
- wall-clock runtime

A fuller limitations inventory is available in [`docs/technical_details.md`](docs/technical_details.md).

## Project status

The current workbench includes:

- a minimal immutable circuit IR
- primitive logical gate definitions
- exact simulation and verification utilities
- multi-controlled Pauli-X construction
- Cuccaro-style modular addition
- primitive logical resource estimation
- Toffoli-expanded analytical T-counts
- single-qubit and tensor-product readout-error mitigation
- reproducible benchmarks and automated tests
- documentation of assumptions and scaling behavior

The project is intentionally small enough to inspect while still demonstrating explicit conventions, testable abstractions, reproducible benchmarks, and honest resource-model boundaries.
