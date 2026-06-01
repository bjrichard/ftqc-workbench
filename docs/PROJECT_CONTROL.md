# FTQC Workbench — Project Control

## Project objective

Build a small, well-tested Python workbench for fault-tolerant quantum computing (FTQC) primitive compilation.

The workbench will support construction, resource estimation, simulation, verification, and benchmarking of selected logical Clifford+T circuit primitives.

The primary project corresponds to the uploaded PDF project “Enabling tools: simulation/verification.” Secondary supported projects include “Local optimizations,” “Clifford circuits,” “Integer and modular adders,” and “Multiply-controlled Toffoli.”

## Default summer path

The default 12-week path is:

1. Build verification and resource-estimation tooling.
2. Implement and verify multi-controlled Toffoli (MCT) circuits.
3. Implement and verify one ripple-carry-style integer adder.
4. Add one simple local optimization pass.
5. Produce benchmarks and a technical report.

All other primitives are stretch goals unless explicitly promoted during weekly review.

## Core deliverable

By the end of the project, the repo should demonstrate:

1. A clean circuit intermediate representation (IR).
2. A basic logical gate library.
3. Clifford+T resource counting.
4. Exact simulation for small circuits.
5. Reversible-circuit verification.
6. At least two implemented primitive families:
   - Required: multi-controlled Toffoli.
   - Required: one integer adder.
7. One simple optimization pass.
8. Benchmark results.
9. A short technical report.

## Time budget

Assume approximately 3 hours/day, 5 days/week.

Target duration: 12 weeks.

Expected total effort: approximately 180 hours.

## In scope

The project may include:

- Circuit IR
- Gate and operation objects
- Clifford+T gate library
- Resource estimation
- Small exact unitary simulation
- Reversible truth-table simulation
- Circuit equivalence checking
- Multi-controlled Toffoli implementation
- One ripple-carry-style integer adder
- One simple local optimization pass
- Benchmark scripts
- Documentation and technical reports

## Default package architecture

Assume the package uses the current repo/package name unless explicitly changed.

Expected structure:

```text
src/
  qc_compiler/
    circuits/
    gates/
    resources/
    simulation/
    verification/
    primitives/
    passes/

tests/
  circuits/
  gates/
  resources/
  simulation/
  verification/
  primitives/
  passes/

docs/
  PROJECT_CONTROL.md
  resource_model.md
  references.md
  backlog.md
  weekly_logs/
```

## Core abstractions

The project should converge toward these explicit objects or close equivalents:

- `Gate`
- `Operation`
- `Circuit`
- `ResourceEstimate`
- `ResourceEstimator`
- `Simulator`
- `Verifier`
- `PrimitiveBuilder`
- `CompilerPass`

Avoid adding new abstractions unless they simplify one of these responsibilities.

## Reference discipline

Each primitive or algorithmic construction must be tied to a source.

For every implemented primitive, add or update `docs/references.md` with:

1. The paper, book, blog post, or documentation source used.
2. The specific construction being implemented.
3. Any assumptions or simplifications made.
4. Whether the implementation is:
   - a direct reproduction,
   - a simplified educational implementation,
   - an adaptation,
   - or original work.
5. Known gaps between the source construction and this implementation.

Do not cite a construction in the README or report unless the relevant source has actually been read closely enough to support the claim.

## Resource model documentation

Maintain `docs/resource_model.md`.

The resource model must explicitly define:

1. Gate set.
2. Which gates are treated as Clifford.
3. Which gates contribute to T-count.
4. Whether T-depth is modeled.
5. How circuit depth is defined.
6. Whether measurements are modeled.
7. Whether feedforward is modeled.
8. How ancillae are counted.
9. Whether dirty ancillae and clean ancillae are distinguished.
10. Whether connectivity is ignored, approximated, or modeled.
11. Whether SWAP overhead is included.
12. Whether global phase is ignored in equivalence checks.

Default assumptions unless changed:

- Logical gate set: Clifford+T.
- Connectivity: ignored in the first implementation.
- Measurements/feedforward: out of scope unless explicitly promoted.
- Ancilla count: clean ancillae only, unless otherwise documented.
- Global phase: ignored for unitary equivalence.
- Resource estimates are logical-level estimates, not surface-code cost estimates.

## Default benchmark sizes

Use fixed default benchmark sizes unless a weekly review changes them.

### Multi-controlled Toffoli

Benchmark number of controls:

- `k = 2, 3, 4, 5, 8, 16`

Verification policy:

- Exhaustive truth-table verification for small `k`.
- Randomized basis-state testing for larger `k`.
- Exact unitary verification only when qubit count is small enough to be practical.

### Integer adder

Benchmark bit widths:

- `n = 2, 3, 4, 8, 16`

Verification policy:

- Exhaustive classical input testing for small `n`.
- Randomized input testing for larger `n`.
- Ancilla cleanup must be tested explicitly.

### Optimization pass

Benchmark on:

- hand-written cancellation examples
- generated random circuits
- MCT circuits
- adder circuits, if available

Report:

- gate count before/after
- T-count before/after
- depth before/after, if depth is implemented
- whether equivalence was verified

## Out of scope

Do not pursue these unless explicitly promoted from the backlog after weekly review:

- Full Shor/Regev compilation
- Full quantum phase estimation
- Hamiltonian simulation algorithms
- Select-V
- GF multiplication/division
- Single-qubit rotation synthesis
- Full Clifford synthesis
- Large-scale decision diagram implementation
- Full graphical circuit visualizer
- General-purpose quantum SDK replacement
- Hardware-level error correction modeling
- Surface-code scheduling
- Magic-state factory modeling
- Full 2D lattice routing implementation

## Stretch goals

Stretch goals are allowed only after the default path is stable.

Possible stretch goals:

- Relative-phase Toffoli variants
- Clifford-only verification or tableau tools
- Approximate QFT benchmark
- Simple 2D nearest-neighbor routing proxy
- Basic circuit visualization
- Comparison against Qiskit or another SDK

## Scope control rule

A new idea may enter the active project only if it directly improves one of the following:

1. Verification tooling
2. Resource estimation
3. Multi-controlled Toffoli implementation
4. Integer adder implementation
5. Local optimization
6. Benchmarking
7. Final technical writeup

Otherwise, place it in `docs/backlog.md`.

## Scope-cut triggers

Use these triggers to protect the project from failure.

1. If exact simulation is not complete by the end of Week 5, defer local optimization.
2. If reversible verification is not complete by the end of Week 6, defer the integer adder.
3. If MCT implementation is not complete by the end of Week 8, defer the integer adder and focus on MCT + verification.
4. If the integer adder is not complete by the end of Week 10, the final report focuses on verification + MCT.
5. If tests are unstable for more than three consecutive work sessions, stop adding features and stabilize the test suite.
6. If a new abstraction causes more confusion than clarity after two sessions, remove or simplify it.
7. If a stretch goal takes more than one session without producing a concrete deliverable, move it back to the backlog.

## Verification standards

Correctness must be tested explicitly.

Use the following standards where applicable:

1. For small general quantum circuits:
   - Verify unitary equivalence up to global phase.
   - Use hand-derived examples where possible.

2. For reversible circuits:
   - Verify truth-table equivalence.
   - Check action on all computational basis states for small `n`.

3. For generated primitives:
   - Test several input sizes.
   - Test edge cases.
   - Use randomized basis-state tests when exhaustive checks become too large.

4. For optimization passes:
   - Verify pre-optimization and post-optimization circuits are equivalent.
   - Compare resources before and after optimization.

5. For resource estimation:
   - Test resource counts against small hand-counted examples.

## Definition of done

A feature is not done until:

1. It has tests.
2. `pytest` passes.
3. Public behavior is documented.
4. Resource accounting is defined if relevant.
5. Correctness assumptions are explicit.
6. Any limitations are written down.
7. The work is committed with a clear commit message.

A benchmark is not done until:

1. It can be run from a clean checkout.
2. The command is documented.
3. The output format is stable.
4. The relevant circuit sizes are specified.
5. Results are saved or summarized in documentation.

The project is not done until:

1. Tests pass.
2. The README explains the project clearly.
3. The technical report summarizes methods, results, limitations, and future work.
4. A reader can reproduce the main results without reading this chat.

## 12-week roadmap

### Weeks 1–2: Circuit and gate foundation

Build the basic code architecture.

Deliverables:

- `Gate`
- `Operation`
- `Circuit`
- qubit indexing conventions
- primitive gate library
- basic append/composition behavior
- unit tests

Definition of done:

- Simple circuits can be constructed.
- Gates and operations can be inspected.
- Invalid operations fail clearly.
- `pytest` passes.

### Week 3: Resource estimation

Add resource-counting tools.

Deliverables:

- `ResourceEstimate`
- `ResourceEstimator`
- gate count
- T-count
- CNOT/CZ count
- simple depth estimate
- ancilla convention

Definition of done:

- Simple circuits produce correct resource summaries.
- Resource counts are tested against hand-counted circuits.
- Resource assumptions are documented in `docs/resource_model.md`.

### Weeks 4–5: Exact simulation and equivalence

Implement small exact simulation.

Deliverables:

- statevector or unitary simulator for small `n`
- circuit-to-unitary conversion
- equivalence checker up to global phase
- tests on known identities

Definition of done:

- Small circuits can be verified against expected unitaries.
- Equivalent circuits are correctly identified.
- Non-equivalent circuits are correctly rejected.

### Week 6: Reversible-circuit verification

Add specialized verification for classical reversible circuits.

Deliverables:

- truth-table simulator
- reversible equivalence checker
- NOT, CNOT, Toffoli, and MCT test cases

Definition of done:

- Reversible circuits can be checked without full unitary simulation.
- Exhaustive truth-table checks work for small `n`.
- Randomized basis-state checks work for larger `n`.

### Weeks 7–8: Multi-controlled Toffoli primitive

Implement and benchmark the first required primitive family.

Deliverables:

- one MCT construction
- source note in `docs/references.md`
- correctness tests across multiple sizes
- resource estimates across benchmark sizes
- benchmark table

Definition of done:

- MCT works for selected values of `k`.
- Correctness is verified.
- Resource scaling is documented.
- Limitations are explicit.

### Weeks 9–10: Integer adder primitive

Implement and benchmark one ripple-carry-style integer adder.

Deliverables:

- one integer adder construction
- source note in `docs/references.md`
- correctness tests across benchmark sizes
- resource estimates across benchmark sizes
- benchmark table

Definition of done:

- The adder works for selected register sizes.
- Reversible correctness is verified.
- Resource scaling is documented.
- Ancilla behavior is explicit.

### Week 11: Local optimization pass

Implement one simple optimization pass.

Default choice:

- cancel adjacent self-inverse gates.

Other acceptable choices:

- remove identity patterns
- simple CNOT cancellation
- small template-based rewrite

Definition of done:

- Pass preserves correctness.
- Pre/post resource counts are compared.
- Tests confirm equivalence.
- The pass is documented as local, simple, and non-exhaustive.

### Week 12: Final report and cleanup

Prepare the repo as a finished artifact.

Deliverables:

- cleaned README
- benchmark results
- final technical report
- backlog of future work
- publication-readiness assessment

Definition of done:

- A reader can understand the project without this chat.
- Tests pass.
- Main results are reproducible.
- The repo is credible as a quantum software engineering portfolio artifact.

## Daily workflow

Each work session should follow this structure:

1. State the day’s goal.
2. Identify the smallest useful deliverable.
3. Review relevant existing code.
4. Write or update tests first when practical.
5. Implement only what is needed for the day’s goal.
6. Run tests.
7. Commit changes.
8. Write a short log entry if useful.

## AI usage rules

The AI should act as a coach, reviewer, and debugging partner.

The AI should not simply dump final code unless explicitly requested.

Preferred pattern:

1. Explain the concept.
2. Ask the user to attempt the implementation.
3. Review the user’s code.
4. Suggest targeted fixes.
5. Provide full code only when the user is blocked, when refactoring is the lesson, or when the user explicitly asks.

The user should do enough implementation to learn the design and debugging process.

## Commit discipline

Use small commits with clear messages.

Examples:

- `feat(circuits): add immutable gate model`
- `feat(resources): count Clifford+T gate resources`
- `test(simulation): verify single-qubit gate matrices`
- `feat(primitives): add multi-controlled Toffoli builder`
- `docs(project): add project control plan`

## Weekly review

At the end of each week, answer:

1. What was completed?
2. What is behind schedule?
3. What should be cut?
4. What should move to backlog?
5. What is next week’s main deliverable?
6. Did any result suggest a publishable angle?
7. Do any scope-cut triggers apply?

Weekly review may modify the plan, but only by explicitly editing this file or moving items to `docs/backlog.md`.

## Publication checkpoints

Do not assume the project is publishable at the start.

At weeks 6, 9, and 12, assess whether there is a credible publishable angle.

A publishable direction requires evidence such as:

1. A nontrivial resource crossover.
2. A verified optimizer not already available in common SDK workflows.
3. A useful benchmark suite with a clearly defined gap.
4. A clarification or reproduction of a confusing claim in the literature.
5. A specialized equivalence-checking workflow that is simpler, faster, or more targeted than obvious alternatives.

If no novel claim appears, the project remains a strong portfolio artifact and technical report.

## Project success criteria

Minimum success:

- Circuit IR works.
- Resource estimation works.
- Exact simulation works for small circuits.
- Reversible verification works.
- One primitive family is implemented and tested.

Strong success:

- MCT and one integer adder are implemented.
- Benchmarks are reproducible.
- One local optimization pass works.
- Final report is clear and technically honest.

Exceptional success:

- A credible workshop-paper direction emerges.
- The repo contains a verified benchmark suite or optimization result that could be developed further.
