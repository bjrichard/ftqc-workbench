from qc_compiler.gates import Gate, CNOT, CZ, H, I, S, T, TOFFOLI, X, Y, Z


def test_primitive_gates_have_expected_names_and_arities():
    """Verify that primitive gates have expected names and arities."""
    expected = {
        I: ("I", 1),
        X: ("X", 1),
        Y: ("Y", 1),
        Z: ("Z", 1),
        H: ("H", 1),
        S: ("S", 1),
        T: ("T", 1),
        CNOT: ("CNOT", 2),
        CZ: ("CZ", 2),
        TOFFOLI: ("TOFFOLI", 3),
    }

    for gate, (name, arity) in expected.items():
        assert gate.name == name
        assert gate.arity == arity


def test_primitive_gates_are_gate_objects():
    """Verify that primitive gates are Gate objects."""
    primitive_gates = (I, X, Y, Z, H, S, T, CNOT, CZ, TOFFOLI)

    for gate in primitive_gates:
        assert isinstance(gate, Gate)


def test_primitive_gates_import_from_package():
    """Verify that primitive gates are exposed through the public gates package."""
    from qc_compiler import gates as gates_package

    assert gates_package.I is I
    assert gates_package.X is X
    assert gates_package.Y is Y
    assert gates_package.Z is Z
    assert gates_package.H is H
    assert gates_package.S is S
    assert gates_package.T is T
    assert gates_package.CNOT is CNOT
    assert gates_package.CZ is CZ
    assert gates_package.TOFFOLI is TOFFOLI
