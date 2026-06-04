from __future__ import annotations

from qc_compiler.gates.gate import Gate


I = Gate(name="I", arity=1)
X = Gate(name="X", arity=1)
Y = Gate(name="Y", arity=1)
Z = Gate(name="Z", arity=1)
H = Gate(name="H", arity=1)
S = Gate(name="S", arity=1)
T = Gate(name="T", arity=1)

CNOT = Gate(name="CNOT", arity=2)
CZ = Gate(name="CZ", arity=2)

TOFFOLI = Gate(name="TOFFOLI", arity=3)
