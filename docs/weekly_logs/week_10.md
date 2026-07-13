# Week 10 log — Toffoli-expanded resource estimates

## Week 10 objective

Improve the resource model by distinguishing primitive logical resource
counts from analytical Toffoli-expanded T-count estimates.

The main motivation was that both implemented reversible primitive families
rely heavily on Toffoli gates:

- clean-ancilla multi-controlled Pauli-X
- Cuccaro-style in-place modular adder

Before Week 10, benchmark tables correctly reported `t_count = 0` because
Toffoli was treated as a primitive logical gate. However, this was easy to
misread as zero fault-tolerant T-cost. Week 10 introduced a separate analytical
expanded estimate to make that distinction explicit.

## Scope for this week

In scope:

- document the primitive-versus-expanded resource-model distinction
- add a Toffoli-expanded resource estimate API
- preserve the existing primitive `ResourceEstimator`
- add tests for expanded T-count behavior
- update benchmark scripts to emit expanded T-counts
- regenerate benchmark comma-separated values (CSV) tables
- update benchmark documentation
- update the central resource-model documentation

Out of scope:

- actual Toffoli circuit decomposition
- Clifford+T circuit rewriting
- T-depth
- Clifford gate counts
- relative-phase Toffoli variants
- dirty-ancilla Toffoli variants
- magic-state distillation cost
- physical qubit estimates
- surface-code distance
- hardware runtime estimates
- routing or topology-aware estimates

## Completed work

### Day 1 — Resource-model design note

Added:

```text
docs/toffoli_resource_model_notes.md
```

The note defines the conceptual split between:

- primitive logical resource estimates
- Toffoli-expanded analytical estimates

The primitive estimate counts exactly what appears in the circuit Intermediate
Representation (IR).

The expanded estimate preserves the primitive estimate and adds a derived
T-count using an explicit Toffoli T-cost convention.

The first convention is:

\[
1\ \mathrm{Toffoli} = 7\ T.
\]

Therefore:

\[
N_T^{\mathrm{expanded}}
=
N_T^{\mathrm{primitive}}
+
7N_{\mathrm{Toffoli}}.
\]

### Day 2 — Expanded resource estimate API

Added:

```text
src/qc_compiler/resources/expanded.py
tests/resources/test_expanded.py
```

Implemented:

```python
estimate_toffoli_expanded_resources(
    circuit: Circuit,
    *,
    toffoli_t_cost: int = 7,
) -> ExpandedResourceEstimate
```

The expanded estimate:

- preserves the primitive `ResourceEstimate`
- computes `expanded_t_count`
- records the Toffoli T-cost convention
- does not mutate or decompose the circuit

Also updated:

```text
src/qc_compiler/resources/__init__.py
```

to export the new expanded resource API while preserving existing public
exports.

### Day 3 — Benchmark integration

Updated the multi-controlled Pauli-X and Cuccaro adder benchmark scripts to
emit:

```text
expanded_t_count
```

Regenerated:

```text
docs/benchmarks/multi_controlled_x.csv
docs/benchmarks/cuccaro_adder.csv
```

Updated benchmark tests to verify the expanded T-count values.

Updated benchmark documentation to explain the distinction between:

- primitive explicit T gates
- analytically expanded Toffoli T-counts

### Day 4 — Central resource-model documentation

Updated:

```text
docs/resource_model.md
```

The resource-model documentation now describes:

- the primitive `ResourceEstimator`
- the separate Toffoli-expanded estimate layer
- the default `1 Toffoli = 7 T` analytical convention
- the fact that `expanded_t_count` is not part of the primitive
  `ResourceEstimate`
- the continued non-goals around actual decomposition, T-depth, and physical
  fault-tolerant resource estimates

## Current implementation status

Implemented:

- primitive logical resource estimates
- Toffoli-expanded analytical T-count estimates
- tests for expanded resource behavior
- benchmark CSV output with expanded T-counts
- benchmark documentation explaining expanded T-counts
- central resource-model documentation reflecting the new estimate layer

Not implemented:

- actual Toffoli decomposition
- Clifford+T circuit expansion
- T-depth
- magic-state resource estimates
- physical resource estimates
- topology-aware scheduling
- routing-aware estimates

## Benchmark impact

The primitive benchmark values remain valid.

The new `expanded_t_count` column provides an analytical companion estimate
under the default Toffoli convention.

For the clean-ancilla multi-controlled Pauli-X construction, for \(k \geq 2\):

\[
N_{\mathrm{Toffoli}} = 2k - 3.
\]

Therefore:

\[
N_T^{\mathrm{expanded}} = 7(2k - 3).
\]

For the general Cuccaro-style adder, for \(n \geq 3\):

\[
N_{\mathrm{Toffoli}} = 2n.
\]

Therefore:

\[
N_T^{\mathrm{expanded}} = 14n.
\]

The compact two-bit adder remains a special case and is reported directly from
the benchmark output rather than included in the general scaling formula.

## Interpretation

Week 10 did not make the resource model physical. It made the logical
bookkeeping more honest.

The project now clearly separates:

```text
What the circuit builder emitted
```

from:

```text
What first-order Toffoli T-cost accounting implies
```

That distinction is important for fault-tolerant quantum computing discussions.
It avoids two bad interpretations:

- treating primitive Toffoli as free
- pretending the project has a full Clifford+T or physical resource model

## End-of-week review

1. What was completed?
   - Toffoli resource-model design note, expanded resource estimate API,
     expanded-resource tests, benchmark CSV updates, benchmark documentation
     updates, and central resource-model documentation updates.

2. What is behind schedule?
   - Nothing material. Week 10 stayed focused on the intended resource-model
     improvement.

3. What should be cut?
   - Nothing from the current path.

4. What should move to backlog?
   - Actual Toffoli decomposition, T-depth, Clifford counts, relative-phase
     Toffoli variants, magic-state cost, and physical resource estimates remain
     deferred.

5. What is next week’s main deliverable?
   - Week 11 should add one near-term quantum engineering component, likely a
     small noise-model or error-mitigation feature, without expanding the
     project into a full simulator stack.

6. Did any result suggest a publishable angle?
   - No. The result is a strong portfolio-quality resource-model improvement,
     not a novel research contribution.

7. Do any scope-cut triggers apply?
   - No.
