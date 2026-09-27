import math

import numpy as np
import pytest

from analysis.metrics.covariance import covariance_determinant, covariance_trace


def test_trace_of_identity():
    assert math.isclose(covariance_trace(np.eye(3)), 3.0)


def test_determinant_of_identity():
    assert math.isclose(covariance_determinant(np.eye(3)), 1.0)


def test_determinant_of_diagonal_matrix():
    p = np.diag([2.0, 5.0])
    assert math.isclose(covariance_determinant(p), 10.0)


def test_non_square_matrix_is_rejected():
    with pytest.raises(ValueError):
        covariance_trace(np.ones((2, 3)))
