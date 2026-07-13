from __future__ import annotations

import pytest

from qc_compiler.circuits import Circuit, Operation
from qc_compiler.gates import CNOT, T, TOFFOLI
from qc_compiler.resources import (
    ExpandedResourceEstimate,
    ResourceEstimate,
    estimate_toffoli_expanded_resources,
)


def test_estimate_toffoli_expanded_resources_preserves_primitive_estimate() -> None:
    """Preserve the primitive logical resource estimate."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(gate=TOFFOLI, qubits=(0, 1, 2)),
        ),
    )

    estimate = estimate_toffoli_expanded_resources(circuit)

    assert isinstance(estimate, ExpandedResourceEstimate)
    assert estimate.primitive == ResourceEstimate(
        logical_qubit_count=3,
        gate_count=1,
        depth=1,
        parallel_depth=1,
        t_count=0,
        cnot_count=0,
        cz_count=0,
        toffoli_count=1,
        ancilla_count=0,
    )

def test_estimate_toffoli_expanded_resources_counts_single_toffoli() -> None:
    """Charge one primitive Toffoli gate the default expanded T-cost."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(gate=TOFFOLI, qubits=(0, 1, 2)),
        ),
    )

    estimate = estimate_toffoli_expanded_resources(circuit)

    assert estimate.expanded_t_count == 7
    assert estimate.toffoli_t_cost == 7
    assert estimate.toffoli_expansion == "toffoli_t_cost=7"


def test_estimate_toffoli_expanded_resources_counts_zero_toffoli_circuit() -> None:
    """Leave expanded T-count unchanged when no Toffoli gates are present."""
    circuit = Circuit(
        num_qubits=2,
        operations=(
            Operation(gate=CNOT, qubits=(0, 1)),
            Operation(gate=T, qubits=(1,)),
        ),
    )

    estimate = estimate_toffoli_expanded_resources(circuit)

    assert estimate.primitive.t_count == 1
    assert estimate.primitive.toffoli_count == 0
    assert estimate.expanded_t_count == 1


def test_estimate_toffoli_expanded_resources_counts_mixed_circuit() -> None:
    """Add explicit T gates and Toffoli-expanded T gates."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(gate=T, qubits=(0,)),
            Operation(gate=CNOT, qubits=(0, 1)),
            Operation(gate=TOFFOLI, qubits=(0, 1, 2)),
            Operation(gate=T, qubits=(2,)),
            Operation(gate=TOFFOLI, qubits=(2, 1, 0)),
        ),
    )

    estimate = estimate_toffoli_expanded_resources(circuit)

    assert estimate.primitive.t_count == 2
    assert estimate.primitive.toffoli_count == 2
    assert estimate.expanded_t_count == 16


def test_estimate_toffoli_expanded_resources_accepts_custom_toffoli_cost() -> None:
    """Use an explicit Toffoli T-cost convention when provided."""
    circuit = Circuit(
        num_qubits=3,
        operations=(
            Operation(gate=TOFFOLI, qubits=(0, 1, 2)),
            Operation(gate=TOFFOLI, qubits=(2, 1, 0)),
        ),
    )

    estimate = estimate_toffoli_expanded_resources(
        circuit,
        toffoli_t_cost=4,
    )

    assert estimate.expanded_t_count == 8
    assert estimate.toffoli_t_cost == 4
    assert estimate.toffoli_expansion == "toffoli_t_cost=4"


@pytest.mark.parametrize(
    "circuit",
    [None, object(), "not a circuit"],
)
def test_estimate_toffoli_expanded_resources_rejects_non_circuit(
    circuit: object,
) -> None:
    """Reject non-circuit inputs."""
    with pytest.raises(TypeError, match="circuit must be a Circuit object."):
        estimate_toffoli_expanded_resources(circuit)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "toffoli_t_cost",
    [True, 7.0, "7"],
)
def test_estimate_toffoli_expanded_resources_rejects_non_integer_toffoli_cost(
    toffoli_t_cost: object,
) -> None:
    """Reject non-integer Toffoli T-cost conventions."""
    circuit = Circuit(num_qubits=1)

    with pytest.raises(TypeError, match="toffoli_t_cost must be an integer."):
        estimate_toffoli_expanded_resources(
            circuit,
            toffoli_t_cost=toffoli_t_cost,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("toffoli_t_cost", [0, -1])
def test_estimate_toffoli_expanded_resources_rejects_nonpositive_toffoli_cost(
    toffoli_t_cost: int,
) -> None:
    """Reject nonpositive Toffoli T-cost conventions."""
    circuit = Circuit(num_qubits=1)

    with pytest.raises(ValueError, match="toffoli_t_cost must be positive."):
        estimate_toffoli_expanded_resources(
            circuit,
            toffoli_t_cost=toffoli_t_cost,
        )
