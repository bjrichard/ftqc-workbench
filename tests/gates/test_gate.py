from dataclasses import FrozenInstanceError

import pytest

from qc_compiler.gates import Gate


def test_gate_constructs_valid_gate():
    """Verify that a valid gate stores its name and arity."""
    g = Gate(name="X", arity=1)

    assert g.name == "X"
    assert g.arity == 1


def test_gate_rejects_empty_name():
    """Verify that an empty gate name is rejected."""
    with pytest.raises(ValueError):
        Gate(name="", arity=1)


def test_gate_rejects_whitespace_only_name():
    """Verify that a whitespace-only gate name is rejected."""
    with pytest.raises(ValueError):
        Gate(name="   ", arity=1)


def test_gate_rejects_non_string_name():
    """Verify that a non-string gate name is rejected."""
    with pytest.raises(ValueError):
        Gate(name=234, arity=1)


def test_gate_rejects_negative_arity():
    """Verify that negative gate arity is rejected."""
    with pytest.raises(ValueError):
        Gate(name="X", arity=-2)


def test_gate_rejects_zero_arity():
    """Verify that zero-arity gates are rejected."""
    with pytest.raises(ValueError):
        Gate(name="X", arity=0)


def test_gate_rejects_non_integer_arity():
    """Verify that non-integer gate arity is rejected."""
    with pytest.raises(ValueError):
        Gate(name="X", arity=1.234)


def test_gate_is_immutable():
    """Verify that gate instances cannot be modified after construction."""
    g = Gate(name="X", arity=1)

    with pytest.raises(FrozenInstanceError):
        g.name = "H"


def test_gate_imports_from_package():
    """Verify that Gate is exposed through the public gates package."""
    from qc_compiler.gates import Gate as ImportedGate

    assert ImportedGate is Gate
