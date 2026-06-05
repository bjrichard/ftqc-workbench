# Application Programming Interface (API) examples

This document shows minimal examples for the public Week 2 circuit and gate interfaces.

## Gate-based circuit construction

```python
from qc_compiler.circuits import Circuit
from qc_compiler.gates import CNOT, X

circuit = Circuit(num_qubits=2)
circuit = circuit.append_gate(gate=X, qubits=(0,))
circuit = circuit.append_gate(gate=CNOT, qubits=(0, 1))

assert len(circuit) == 2
```

## Operation-based circuit construction

```python
from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, X

operations = (
    Operation(gate=X, qubits=(0,)),
    Operation(gate=CNOT, qubits=(0, 1)),
)

circuit = Circuit(num_qubits=2).extend(operations=operations)

assert circuit.operations == operations
```

## Import conventions

Use subpackage imports:

```python
from qc_compiler.gates import X, CNOT
from qc_compiler.circuits import Circuit, Operation
```

Avoid top-level imports for now:

```python
# Not currently supported
from qc_compiler import Circuit, X
```
