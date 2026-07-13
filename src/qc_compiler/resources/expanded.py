from __future__ import annotations

from dataclasses import dataclass

from qc_compiler.circuits import Circuit
from qc_compiler.resources.estimator import ResourceEstimate, ResourceEstimator


@dataclass(frozen=True)
class ExpandedResourceEstimate:
    """Resource estimate with analytical Toffoli expansion.

    Parameters
    ----------
    primitive
        Primitive logical resource estimate computed directly from the circuit
        Intermediate Representation (IR).
    expanded_t_count
        T-count after analytically charging each primitive Toffoli gate a fixed
        T-cost.
    toffoli_t_cost
        Number of T gates assigned to each primitive Toffoli operation.
    toffoli_expansion
        Human-readable name of the Toffoli expansion convention.

    Notes
    -----
    This estimate does not mutate or decompose the input circuit. It preserves
    the primitive estimate and adds a derived T-count under an explicit
    Toffoli expansion convention.
    """

    primitive: ResourceEstimate
    expanded_t_count: int
    toffoli_t_cost: int
    toffoli_expansion: str


def estimate_toffoli_expanded_resources(
    circuit: Circuit,
    *,
    toffoli_t_cost: int = 7,
) -> ExpandedResourceEstimate:
    """Estimate resources with analytical Toffoli T-cost expansion.

    Parameters
    ----------
    circuit
        Circuit whose resources should be estimated.
    toffoli_t_cost
        Number of T gates assigned to each primitive Toffoli operation. The
        default value, 7, corresponds to the standard exact Toffoli T-count
        convention used as the project's first expanded resource model.

    Returns
    -------
    ExpandedResourceEstimate
        Primitive resource estimate plus a derived expanded T-count.

    Raises
    ------
    TypeError
        If ``circuit`` is not a ``Circuit`` object.
    TypeError
        If ``toffoli_t_cost`` is not an integer or is a Boolean.
    ValueError
        If ``toffoli_t_cost`` is not positive.

    Notes
    -----
    The expanded T-count is computed as

    ``primitive.t_count + toffoli_t_cost * primitive.toffoli_count``.

    The input circuit is not rewritten. No Clifford count, T-depth, physical
    resource estimate, magic-state cost, routing overhead, or hardware timing
    model is inferred.
    """
    if not isinstance(circuit, Circuit):
        raise TypeError("circuit must be a Circuit object.")

    if isinstance(toffoli_t_cost, bool) or not isinstance(toffoli_t_cost, int):
        raise TypeError("toffoli_t_cost must be an integer.")

    if toffoli_t_cost <= 0:
        raise ValueError("toffoli_t_cost must be positive.")

    primitive = ResourceEstimator().estimate(circuit)

    return ExpandedResourceEstimate(
        primitive=primitive,
        expanded_t_count=(
            primitive.t_count + toffoli_t_cost * primitive.toffoli_count
        ),
        toffoli_t_cost=toffoli_t_cost,
        toffoli_expansion=f"toffoli_t_cost={toffoli_t_cost}",
    )
