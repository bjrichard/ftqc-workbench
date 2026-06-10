import numpy as np
import pytest

from qc_compiler.gates.gate import Gate
from qc_compiler.gates.library import CNOT, CZ, H, I, S, T, X, Y, Z
from qc_compiler.simulation import get_gate_matrix


def test_get_gate_matrix_returns_identity_matrix():
    """Verify that the identity gate matrix is returned."""
    expected = np.array(
        [
            [1, 0],
            [0, 1],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(get_gate_matrix(gate=I), expected)


def test_get_gate_matrix_returns_x_matrix():
    """Verify that the Pauli-X gate matrix is returned."""
    expected = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(get_gate_matrix(gate=X), expected)


def test_get_gate_matrix_returns_y_matrix():
    """Verify that the Pauli-Y gate matrix is returned."""
    expected = np.array(
        [
            [0, -1j],
            [1j, 0],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(get_gate_matrix(gate=Y), expected)


def test_get_gate_matrix_returns_z_matrix():
    """Verify that the Pauli-Z gate matrix is returned."""
    expected = np.array(
        [
            [1, 0],
            [0, -1],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(get_gate_matrix(gate=Z), expected)


def test_get_gate_matrix_returns_h_matrix():
    """Verify that the Hadamard gate matrix is returned."""
    expected = (1 / np.sqrt(2)) * np.array(
        [
            [1, 1],
            [1, -1],
        ],
        dtype=complex,
    )

    np.testing.assert_allclose(get_gate_matrix(gate=H), expected)


def test_get_gate_matrix_returns_s_matrix():
    """Verify that the phase gate matrix is returned."""
    expected = np.array(
        [
            [1, 0],
            [0, 1j],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(get_gate_matrix(gate=S), expected)


def test_get_gate_matrix_returns_t_matrix():
    """Verify that the T gate matrix is returned."""
    expected = np.array(
        [
            [1, 0],
            [0, np.exp(1j * np.pi / 4)],
        ],
        dtype=complex,
    )

    np.testing.assert_allclose(get_gate_matrix(gate=T), expected)


def test_get_gate_matrix_returns_cnot_matrix():
    """Verify that the controlled-NOT matrix follows the little-endian convention."""
    expected = np.array(
        [
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(get_gate_matrix(gate=CNOT), expected)


def test_get_gate_matrix_returns_cz_matrix():
    """Verify that the controlled-Z matrix is returned."""
    expected = np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, -1],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(get_gate_matrix(gate=CZ), expected)


def test_get_gate_matrix_returns_complex_numpy_array():
    """Verify that gate matrices are returned as complex NumPy arrays."""
    matrix = get_gate_matrix(gate=X)

    assert isinstance(matrix, np.ndarray)
    assert matrix.dtype == complex


def test_get_gate_matrix_returns_copy():
    """Verify that modifying a returned matrix does not corrupt future calls."""
    matrix = get_gate_matrix(gate=X)
    matrix[0, 0] = 999

    fresh_matrix = get_gate_matrix(gate=X)
    expected = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=complex,
    )

    np.testing.assert_array_equal(fresh_matrix, expected)


def test_get_gate_matrix_rejects_non_gate_input():
    """Verify that non-Gate inputs are rejected."""
    with pytest.raises(TypeError):
        get_gate_matrix("not a gate")


def test_get_gate_matrix_rejects_unsupported_gate():
    """Verify that unsupported gates are rejected."""
    unsupported_gate = Gate(name="DUMMY_GATE", arity=14)

    with pytest.raises(ValueError):
        get_gate_matrix(gate=unsupported_gate)


def test_get_gate_matrix_accepts_equivalent_gate_value():
    """Verify that equivalent Gate values resolve to the same matrix."""
    expected = get_gate_matrix(gate=I)
    actual = get_gate_matrix(gate=Gate(name="I", arity=1))

    np.testing.assert_array_equal(actual, expected)


def test_get_gate_matrix_imports_from_package():
    """Verify that get_gate_matrix is exposed through the simulation package."""
    from qc_compiler.simulation import get_gate_matrix as imported_get_gate_matrix

    assert imported_get_gate_matrix is get_gate_matrix
