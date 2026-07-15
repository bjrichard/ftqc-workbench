from __future__ import annotations

import numpy as np
import pytest

from qc_compiler.mitigation import (
    mitigate_single_qubit_readout,
    mitigate_tensor_product_readout,
)


def test_identity_assignment_matrix_returns_observed_probabilities() -> None:
    """Return observed probabilities when the assignment matrix is identity."""
    result = mitigate_single_qubit_readout(
        counts={"0": 75, "1": 25},
        assignment_matrix=np.eye(2),
    )

    assert result == {
        "0": pytest.approx(0.75),
        "1": pytest.approx(0.25),
    }


def test_symmetric_readout_error_corrects_expected_direction() -> None:
    """Correct a hand-computable symmetric readout-error example."""
    assignment_matrix = np.array(
        [
            [0.9, 0.1],
            [0.1, 0.9],
        ],
        dtype=float,
    )

    result = mitigate_single_qubit_readout(
        counts={"0": 820, "1": 180},
        assignment_matrix=assignment_matrix,
    )

    assert result == {
        "0": pytest.approx(0.9),
        "1": pytest.approx(0.1),
    }


@pytest.mark.parametrize(
    ("counts", "expected"),
    [
        ({"0": 100}, {"0": 1.0, "1": 0.0}),
        ({"1": 100}, {"0": 0.0, "1": 1.0}),
    ],
)
def test_missing_outcomes_are_treated_as_zero(
    counts: dict[str, int],
    expected: dict[str, float],
) -> None:
    """Treat missing single-qubit count outcomes as zero counts."""
    result = mitigate_single_qubit_readout(
        counts=counts,
        assignment_matrix=np.eye(2),
    )

    assert result == {
        "0": pytest.approx(expected["0"]),
        "1": pytest.approx(expected["1"]),
    }


def test_output_probabilities_sum_to_one() -> None:
    """Return a normalized mitigated probability distribution."""
    assignment_matrix = np.array(
        [
            [0.95, 0.2],
            [0.05, 0.8],
        ],
        dtype=float,
    )

    result = mitigate_single_qubit_readout(
        counts={"0": 80, "1": 20},
        assignment_matrix=assignment_matrix,
    )

    assert set(result) == {"0", "1"}
    assert sum(result.values()) == pytest.approx(1.0)


def test_negative_linear_inversion_entries_are_clipped_and_renormalized() -> None:
    """Clip negative mitigated entries and renormalize the distribution."""
    assignment_matrix = np.array(
        [
            [0.9, 0.2],
            [0.1, 0.8],
        ],
        dtype=float,
    )

    result = mitigate_single_qubit_readout(
        counts={"0": 100, "1": 0},
        assignment_matrix=assignment_matrix,
    )

    assert result == {
        "0": pytest.approx(1.0),
        "1": pytest.approx(0.0),
    }


@pytest.mark.parametrize(
    "counts",
    [
        None,
        [("0", 1)],
        "not counts",
    ],
)
def test_rejects_non_dictionary_counts(counts: object) -> None:
    """Reject measured counts that are not dictionaries."""
    with pytest.raises(TypeError, match="counts must be a dictionary."):
        mitigate_single_qubit_readout(  # type: ignore[arg-type]
            counts=counts,
            assignment_matrix=np.eye(2),
        )


def test_rejects_non_string_count_keys() -> None:
    """Reject count dictionaries with non-string keys."""
    with pytest.raises(TypeError, match="count keys must be strings."):
        mitigate_single_qubit_readout(  # type: ignore[arg-type]
            counts={0: 1},
            assignment_matrix=np.eye(2),
        )


def test_rejects_invalid_count_keys() -> None:
    """Reject bitstrings outside the single-qubit output alphabet."""
    with pytest.raises(ValueError, match='count keys must be "0" or "1".'):
        mitigate_single_qubit_readout(
            counts={"00": 1},
            assignment_matrix=np.eye(2),
        )


@pytest.mark.parametrize(
    "counts",
    [
        {"0": 1.5},
        {"0": True},
        {"0": "1"},
    ],
)
def test_rejects_non_integer_count_values(counts: dict[str, object]) -> None:
    """Reject count values that are not non-Boolean integers."""
    with pytest.raises(TypeError, match="count values must be integers."):
        mitigate_single_qubit_readout(  # type: ignore[arg-type]
            counts=counts,
            assignment_matrix=np.eye(2),
        )


def test_rejects_negative_count_values() -> None:
    """Reject negative count values."""
    with pytest.raises(ValueError, match="count values must be nonnegative."):
        mitigate_single_qubit_readout(
            counts={"0": -1},
            assignment_matrix=np.eye(2),
        )


@pytest.mark.parametrize(
    "counts",
    [
        {},
        {"0": 0},
        {"1": 0},
        {"0": 0, "1": 0},
    ],
)
def test_rejects_counts_with_zero_total_shots(
    counts: dict[str, int],
) -> None:
    """Reject empty or all-zero measured counts."""
    with pytest.raises(
        ValueError,
        match="counts must contain at least one shot.",
    ):
        mitigate_single_qubit_readout(
            counts=counts,
            assignment_matrix=np.eye(2),
        )


@pytest.mark.parametrize(
    "assignment_matrix",
    [
        None,
        [[1.0, 0.0], [0.0, 1.0]],
        "not a matrix",
    ],
)
def test_rejects_non_numpy_assignment_matrix(
    assignment_matrix: object,
) -> None:
    """Reject assignment matrices that are not NumPy arrays."""
    with pytest.raises(
        TypeError,
        match="assignment_matrix must be a NumPy array.",
    ):
        mitigate_single_qubit_readout(  # type: ignore[arg-type]
            counts={"0": 1},
            assignment_matrix=assignment_matrix,
        )


@pytest.mark.parametrize(
    "assignment_matrix",
    [
        np.array([1.0, 0.0]),
        np.ones((2, 3)),
        np.ones((1, 2)),
    ],
)
def test_rejects_assignment_matrix_with_wrong_shape(
    assignment_matrix: np.ndarray,
) -> None:
    """Reject assignment matrices that are not two-by-two."""
    with pytest.raises(
        ValueError,
        match=r"assignment_matrix must have shape \(2, 2\).",
    ):
        mitigate_single_qubit_readout(
            counts={"0": 1},
            assignment_matrix=assignment_matrix,
        )


def test_rejects_nonnumeric_assignment_matrix() -> None:
    """Reject assignment matrices with nonnumeric dtype."""
    assignment_matrix = np.array(
        [
            ["a", "b"],
            ["c", "d"],
        ],
    )

    with pytest.raises(ValueError, match="assignment_matrix must be numeric."):
        mitigate_single_qubit_readout(
            counts={"0": 1},
            assignment_matrix=assignment_matrix,
        )


@pytest.mark.parametrize(
    "assignment_matrix",
    [
        np.array([[np.nan, 0.0], [0.0, 1.0]]),
        np.array([[np.inf, 0.0], [0.0, 1.0]]),
    ],
)
def test_rejects_nonfinite_assignment_matrix(
    assignment_matrix: np.ndarray,
) -> None:
    """Reject assignment matrices containing NaN or infinity."""
    with pytest.raises(
        ValueError,
        match="assignment_matrix must contain finite values.",
    ):
        mitigate_single_qubit_readout(
            counts={"0": 1},
            assignment_matrix=assignment_matrix,
        )


def test_rejects_negative_assignment_matrix_entries() -> None:
    """Reject assignment matrices with negative probabilities."""
    assignment_matrix = np.array(
        [
            [1.1, 0.0],
            [-0.1, 1.0],
        ],
        dtype=float,
    )

    with pytest.raises(
        ValueError,
        match="assignment_matrix entries must be nonnegative.",
    ):
        mitigate_single_qubit_readout(
            counts={"0": 1},
            assignment_matrix=assignment_matrix,
        )


def test_rejects_assignment_matrix_columns_that_do_not_sum_to_one() -> None:
    """Reject assignment matrices whose columns are not probability vectors."""
    assignment_matrix = np.array(
        [
            [0.9, 0.1],
            [0.2, 0.9],
        ],
        dtype=float,
    )

    with pytest.raises(
        ValueError,
        match="assignment_matrix columns must sum to one.",
    ):
        mitigate_single_qubit_readout(
            counts={"0": 1},
            assignment_matrix=assignment_matrix,
        )


def test_rejects_singular_assignment_matrix() -> None:
    """Reject singular assignment matrices."""
    assignment_matrix = np.array(
        [
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        dtype=float,
    )

    with pytest.raises(ValueError, match="assignment_matrix must be invertible."):
        mitigate_single_qubit_readout(
            counts={"0": 1},
            assignment_matrix=assignment_matrix,
        )


def test_tensor_product_identity_assignment_returns_observed_probabilities() -> None:
    """Return observed probabilities for identity multi-qubit assignment."""
    result = mitigate_tensor_product_readout(
        counts={"00": 50, "01": 25, "10": 25},
        assignment_matrices=(np.eye(2), np.eye(2)),
    )

    assert result == {
        "00": pytest.approx(0.5),
        "01": pytest.approx(0.25),
        "10": pytest.approx(0.25),
        "11": pytest.approx(0.0),
    }


def test_tensor_product_readout_matches_single_qubit_on_one_qubit() -> None:
    """Match the single-qubit helper for one assignment matrix."""
    assignment_matrix = np.array(
        [
            [0.9, 0.1],
            [0.1, 0.9],
        ],
        dtype=float,
    )

    tensor_result = mitigate_tensor_product_readout(
        counts={"0": 820, "1": 180},
        assignment_matrices=(assignment_matrix,),
    )
    single_result = mitigate_single_qubit_readout(
        counts={"0": 820, "1": 180},
        assignment_matrix=assignment_matrix,
    )

    assert tensor_result == {
        "0": pytest.approx(single_result["0"]),
        "1": pytest.approx(single_result["1"]),
    }


def test_tensor_product_readout_corrects_independent_two_qubit_error() -> None:
    """Correct a two-qubit product readout-error example."""
    assignment_matrix = np.array(
        [
            [0.9, 0.1],
            [0.1, 0.9],
        ],
        dtype=float,
    )

    result = mitigate_tensor_product_readout(
        counts={
            "00": 8100,
            "01": 900,
            "10": 900,
            "11": 100,
        },
        assignment_matrices=(assignment_matrix, assignment_matrix),
    )

    assert result == {
        "00": pytest.approx(1.0),
        "01": pytest.approx(0.0),
        "10": pytest.approx(0.0),
        "11": pytest.approx(0.0),
    }


def test_tensor_product_readout_returns_all_bitstrings() -> None:
    """Return all bitstrings for the inferred number of qubits."""
    result = mitigate_tensor_product_readout(
        counts={"11": 10},
        assignment_matrices=(np.eye(2), np.eye(2)),
    )

    assert tuple(result) == ("00", "01", "10", "11")
    assert result["11"] == pytest.approx(1.0)


def test_tensor_product_readout_rejects_empty_assignment_matrix_tuple() -> None:
    """Reject empty tensor-product readout models."""
    with pytest.raises(
        ValueError,
        match="assignment_matrices must be nonempty.",
    ):
        mitigate_tensor_product_readout(
            counts={"0": 1},
            assignment_matrices=(),
        )


def test_tensor_product_readout_rejects_non_tuple_assignment_matrices() -> None:
    """Reject non-tuple assignment-matrix collections."""
    with pytest.raises(
        TypeError,
        match="assignment_matrices must be a tuple.",
    ):
        mitigate_tensor_product_readout(  # type: ignore[arg-type]
            counts={"0": 1},
            assignment_matrices=[np.eye(2)],
        )


def test_tensor_product_readout_rejects_wrong_bitstring_length() -> None:
    """Reject count keys that do not match the number of assignment matrices."""
    with pytest.raises(
        ValueError,
        match="count keys must have length 2.",
    ):
        mitigate_tensor_product_readout(
            counts={"0": 1},
            assignment_matrices=(np.eye(2), np.eye(2)),
        )
