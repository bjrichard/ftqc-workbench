# References

## Multi-controlled Pauli-X construction

A. Barenco, C. H. Bennett, R. Cleve, D. P. DiVincenzo, N. Margolus,
P. Shor, T. Sleator, J. A. Smolin, and H. Weinfurter, “Elementary gates
for quantum computation,” *Physical Review A*, 52, 3457–3467 (1995).
arXiv:quant-ph/9503016. DOI: 10.1103/PhysRevA.52.3457.

The paper develops generalized controlled-unitary and Deutsch-Toffoli gate
constructions and analyzes their decomposition into smaller gates.

### Construction used in this project

The workbench implements a simplified educational clean-ancilla
compute-use-uncompute construction for a multi-controlled Pauli-X operation.

For \(k \geq 3\) controls, the implementation:

1. computes successive conjunctions of the controls into \(k-2\) clean
   ancillas
2. applies one Toffoli gate to the target
3. reverses the computation to restore every ancilla to zero

The resulting circuit contains \(2k-3\) Toffoli gates.

### Relationship to the source

This implementation should be described as an educational adaptation of the
standard ancilla-assisted generalized Toffoli construction, not as a
line-for-line reproduction of a specific circuit listing.

The implementation works at the logical Toffoli level. It does not reproduce
the paper’s complete decomposition into one- and two-qubit elementary gates.

### Assumptions and limitations

- Every declared ancilla begins in \(|0\rangle\).
- Every ancilla is restored to \(|0\rangle\).
- Ancillas are clean rather than dirty or borrowed.
- Connectivity is unrestricted.
- Toffoli is treated as a primitive logical operation.
- Clifford+T decomposition cost and T-depth are not modeled.
- Alternative constructions with different ancilla, gate-count, or depth
  tradeoffs are not implemented.

## Cuccaro ripple-carry adder

S. A. Cuccaro, T. G. Draper, S. A. Kutin, and D. P. Moulton,
“A new quantum ripple-carry addition circuit,” arXiv:quant-ph/0410184
(2004).

This project will use the Cuccaro-Draper-Kutin-Moulton ripple-carry adder as
the source for the first reversible integer-adder primitive.

The intended implementation is an educational implementation of the in-place
modular adder using the project’s existing Controlled-NOT (CNOT) and Toffoli
gates. The first implementation will not model Clifford+T decomposition,
T-depth, routing, physical qubits, or fault-tolerant execution cost.
