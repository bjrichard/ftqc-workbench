# Integer adder notes

## Objective

Implement and verify one reversible ripple-carry-style integer adder for the FTQC workbench.

The adder should become the second required primitive family after the clean-ancilla multi-controlled Pauli-X construction.

## Candidate construction

Default construction: Cuccaro-style ripple-carry adder.

The implementation should be treated as a sourced reversible arithmetic primitive, not as an original adder design.

## Intended behavior

For two n-bit input registers `a` and `b`, the adder should implement an in-place modular addition of the form:

\[
|a\rangle |b\rangle \mapsto |a\rangle |a + b \bmod 2^n\rangle.
\]

The `a` register is preserved. The `b` register is overwritten with the sum.

## Register layout

Tentative layout:

- `a`: n qubits
- `b`: n qubits
- carry/work qubits: to be determined after reading the source construction

The exact qubit ordering should be fixed before implementation.

## Gate set

The implementation should use the project’s existing reversible primitive gates:

- Pauli-X if needed
- Controlled-NOT (CNOT)
- Toffoli

No new gate should be added unless required by the selected construction.

## Verification strategy

For small bit widths, verify exhaustively over all computational-basis inputs.

Default small sizes:

- n = 2
- n = 3
- n = 4

For larger sizes, use deterministic randomized basis-state tests.

Default larger sizes:

- n = 8
- n = 16

Verification must check:

- the `a` register is preserved
- the `b` register contains `(a + b) mod 2**n`
- any declared work qubits are restored to their required final values

## Benchmark strategy

Benchmark sizes should follow the project roadmap:

- n = 2
- n = 3
- n = 4
- n = 8
- n = 16

Record:

- logical qubit count
- gate count
- CNOT count
- Toffoli count
- T count
- serial depth
- dependency-preserving parallel depth
- declared clean ancilla or work-qubit requirements

## Open decisions

- exact Cuccaro variant to implement
- whether to include an incoming carry qubit
- whether to expose a final carry-out qubit
- whether the operation should be modular addition or full addition with carry-out
- exact register ordering
- exact source citation and relationship to the implemented circuit

## Out of scope for the first adder

- subtraction
- controlled addition
- modular reduction
- multiplication
- quantum Fourier transform adders
- dirty-ancilla arithmetic
- Clifford+T decomposition of Toffoli
- routing-aware arithmetic costs
