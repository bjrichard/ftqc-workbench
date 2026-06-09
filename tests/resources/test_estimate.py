from dataclasses import FrozenInstanceError

import pytest

from qc_compiler.resources import ResourceEstimate


def test_resource_estimate_constructs_valid_estimate():
    """Verify that a valid resource estimate stores all count fields."""
    estimate = ResourceEstimate(
        gate_count=3,
        t_count=1,
        cnot_count=1,
        cz_count=0,
        logical_qubit_count=2,
        ancilla_count=0,
        depth=3,
    )

    assert estimate.gate_count == 3
    assert estimate.t_count == 1
    assert estimate.cnot_count == 1
    assert estimate.cz_count == 0
    assert estimate.logical_qubit_count == 2
    assert estimate.ancilla_count == 0
    assert estimate.depth == 3


def test_resource_estimate_allows_none_depth():
    """Verify that depth may be omitted when no depth model has been applied."""
    estimate = ResourceEstimate(
        gate_count=0,
        t_count=0,
        cnot_count=0,
        cz_count=0,
        logical_qubit_count=0,
        ancilla_count=0,
        depth=None,
    )

    assert estimate.depth is None


def test_resource_estimate_rejects_non_integer_gate_count():
    """Verify that total gate count must be an integer."""
    with pytest.raises(TypeError):
        ResourceEstimate(
            gate_count=1.5,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_non_integer_t_count():
    """Verify that T-count must be an integer."""
    with pytest.raises(TypeError):
        ResourceEstimate(
            gate_count=0,
            t_count=1.5,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_non_integer_cnot_count():
    """Verify that controlled-NOT count must be an integer."""
    with pytest.raises(TypeError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=1.5,
            cz_count=0,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_non_integer_cz_count():
    """Verify that controlled-Z count must be an integer."""
    with pytest.raises(TypeError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=1.5,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_non_integer_logical_qubit_count():
    """Verify that logical qubit count must be an integer."""
    with pytest.raises(TypeError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=1.5,
        )


def test_resource_estimate_rejects_non_integer_ancilla_count():
    """Verify that ancilla count must be an integer."""
    with pytest.raises(TypeError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
            ancilla_count=1.5,
        )


def test_resource_estimate_rejects_non_integer_depth():
    """Verify that depth must be an integer or None."""
    with pytest.raises(TypeError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
            depth=1.5,
        )


def test_resource_estimate_rejects_negative_gate_count():
    """Verify that negative total gate counts are rejected."""
    with pytest.raises(ValueError):
        ResourceEstimate(
            gate_count=-1,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_negative_t_count():
    """Verify that negative T-counts are rejected."""
    with pytest.raises(ValueError):
        ResourceEstimate(
            gate_count=0,
            t_count=-1,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_negative_cnot_count():
    """Verify that negative controlled-NOT counts are rejected."""
    with pytest.raises(ValueError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=-1,
            cz_count=0,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_negative_cz_count():
    """Verify that negative controlled-Z counts are rejected."""
    with pytest.raises(ValueError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=-1,
            logical_qubit_count=0,
        )


def test_resource_estimate_rejects_negative_logical_qubit_count():
    """Verify that negative logical qubit counts are rejected."""
    with pytest.raises(ValueError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=-1,
        )


def test_resource_estimate_rejects_negative_ancilla_count():
    """Verify that negative ancilla counts are rejected."""
    with pytest.raises(ValueError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
            ancilla_count=-1,
        )


def test_resource_estimate_rejects_negative_depth():
    """Verify that negative depth estimates are rejected."""
    with pytest.raises(ValueError):
        ResourceEstimate(
            gate_count=0,
            t_count=0,
            cnot_count=0,
            cz_count=0,
            logical_qubit_count=0,
            depth=-1,
        )


def test_resource_estimate_is_immutable():
    """Verify that resource estimates cannot be modified after construction."""
    estimate = ResourceEstimate(
        gate_count=3,
        t_count=1,
        cnot_count=1,
        cz_count=0,
        logical_qubit_count=2,
        ancilla_count=0,
        depth=3,
    )

    with pytest.raises(FrozenInstanceError):
        estimate.gate_count = 4


def test_resource_estimate_imports_from_package():
    """Verify that ResourceEstimate is exposed through the public resources package."""
    from qc_compiler.resources import ResourceEstimate as ImportedResourceEstimate

    assert ImportedResourceEstimate is ResourceEstimate
