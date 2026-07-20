# Final project audit

## Purpose

This audit records the final state of the Fault-Tolerant Quantum Computing
(FTQC) workbench before Week 12 portfolio polish.

The goal is to identify what is implemented, what is tested, what is documented,
what is benchmarked, and what should remain future work.

## Implemented components

### Circuit intermediate representation

Implemented:

- immutable circuit objects
- primitive operations
- named gates
- validation of qubit indices and gate arity
- basic circuit construction patterns

Relevant package areas:

```text
src/qc_compiler/circuits
src/qc_compiler/gates
```

### Gate library

Implemented gate family:

- identity gate
- Pauli gates
- Hadamard gate
- phase gates
- controlled gates
- Toffoli gate

Current scope:

- explicit matrix definitions where practical
- primitive gate objects used by circuits, simulators, builders, and resource
  estimators

### Simulation

Implemented:

- exact statevector simulation
- basis-state simulation
- basis-state permutation utilities
- support for primitive gates used by the workbench

Relevant package area:

```text
src/qc_compiler/simulation
```

### Circuit builders

Implemented:

- clean-ancilla multi-controlled Pauli-X construction
- Cuccaro-style modular ripple-carry adder

Relevant package area:

```text
src/qc_compiler/circuits
```

### Resource estimation

Implemented:

- primitive gate counts
- CNOT counts
- CZ counts
- Toffoli counts
- primitive T-counts
- serial depth
- dependency-preserving parallel depth
- analytical Toffoli-expanded T-count estimates

Relevant package area:

```text
src/qc_compiler/resources
```

### Benchmarks

Implemented benchmark artifacts for:

- clean-ancilla multi-controlled Pauli-X
- Cuccaro-style modular adder

Relevant files:

```text
benchmarks/benchmark_multi_controlled_x.py
benchmarks/benchmark_cuccaro_adder.py
docs/benchmarks/multi_controlled_x.csv
docs/benchmarks/multi_controlled_x.md
docs/benchmarks/cuccaro_adder.csv
docs/benchmarks/cuccaro_adder.md
```

### Readout-error mitigation

Implemented:

- single-qubit readout mitigation
- tensor-product multi-qubit readout mitigation for independent per-qubit
  assignment matrices
- explicit bitstring ordering convention
- validation for count dictionaries and assignment matrices
- linear inversion using `np.linalg.solve`
- clipping and renormalization convention

Relevant package area:

```text
src/qc_compiler/mitigation
```

## Tested components

The project includes tests for:

- gate definitions
- circuit validation
- statevector simulation
- basis-state simulation
- primitive resource estimation
- parallel-depth estimation
- expanded Toffoli T-count estimation
- multi-controlled Pauli-X construction
- Cuccaro adder behavior
- benchmark outputs
- readout-error mitigation

Validation command:

```bash
pytest -q
```

Static checks:

```bash
ruff check .
mypy src
```

## Documented components

Documentation exists for:

- project overview
- technical details
- simulation conventions
- resource model
- source references
- benchmark interpretation
- multi-controlled Pauli-X construction
- Cuccaro adder construction
- readout-error mitigation
- weekly progress logs

Documentation should be checked for consistency across:

- terminology
- file paths
- gate names
- implemented versus future scope
- primitive versus expanded resource estimates
- bitstring and indexing conventions

## Benchmark status

Benchmarks currently cover reusable primitive families rather than arbitrary
applications.

Implemented benchmark families:

- multi-controlled Pauli-X over selected control counts
- Cuccaro modular adder over selected register widths

The benchmark outputs are deterministic and stored in `docs/benchmarks`.

The benchmark tables should be treated as portfolio artifacts, not performance
claims about hardware execution.

## Current limitations

The workbench does not currently support:

- general circuit composition
- arbitrary controlled-unitary synthesis
- routing to hardware coupling maps
- scheduling with hardware durations
- Clifford+T circuit decomposition
- T-depth estimation
- physical qubit estimates
- magic-state factory estimates
- correlated readout-error mitigation
- noisy statevector or density-matrix simulation
- integration with Qiskit, Cirq, Braket, or hardware providers

These are appropriate future-work items. They should not be rushed into the
final week.

## Final Week 12 polish targets

Priority 1:

- ensure `pytest -q` passes
- ensure `ruff check .` passes
- ensure README installation and validation commands are accurate
- ensure README links to benchmark docs and technical docs
- ensure future-work language does not imply unimplemented features exist

Priority 2:

- review `docs/technical_details.md`
- review `docs/resource_model.md`
- review `docs/benchmarks/*.md`
- review readout mitigation docs for bitstring convention consistency

Priority 3:

- add a final project summary
- add a short future-work roadmap
- add a final Week 12 log

## Portfolio assessment

The strongest signal in this project is not the size of the codebase. It is the
combination of:

- explicit conventions
- tested quantum primitives
- deterministic benchmarks
- resource-estimation discipline
- clean separation between ideal simulation, resource modeling, and mitigation
- honest documentation of limitations

The final polish should reinforce that signal.
