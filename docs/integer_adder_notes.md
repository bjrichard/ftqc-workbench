# Integer adder notes

## Objective

Implement and verify one reversible ripple-carry-style integer adder for the FTQC workbench.

The adder should become the second required primitive family after the clean-ancilla multi-controlled Pauli-X construction.

## Selected construction

The selected construction is the Cuccaro-Draper-Kutin-Moulton ripple-carry adder from “A new quantum ripple-carry addition circuit” (`quant-ph/0410184`).

The first implementation will target in-place modular addition:

\[
|a\rangle |b\rangle \mapsto |a\rangle |a+b \bmod 2^n\rangle.
\]

The implementation will use the project’s existing reversible primitive gates:

- Controlled-NOT (CNOT)
- Toffoli

The first implementation will not expose a carry-in or carry-out interface. Those variants can be added later after the base modular adder is verified.

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
- Controlled-NOT (CNOT) count
- Toffoli count
- T count
- serial depth
- dependency-preserving parallel depth
- declared clean ancilla or work-qubit requirements

## Open decisions

- exact register ordering
- whether the implementation should first build an internal non-modular full adder and then expose only the modular interface
- exact relationship between the implemented circuit and the source circuit diagram
- whether helper functions should expose majority and unmajority operations directly

## Deferred variants

- carry-in addition
- carry-out addition
- non-modular addition with explicit overflow qubit
- controlled addition
- subtraction

## Out of scope for the first adder

- modular reduction
- multiplication
- quantum Fourier transform adders
- dirty-ancilla arithmetic
- Clifford+T decomposition of Toffoli
- routing-aware arithmetic costs
- physical fault-tolerant resource estimation
