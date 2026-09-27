import math

import numpy as np
import pytest

from analysis.metrics.estimation_error import position_error, rmse, squared_error


def test_position_error_of_identical_points_is_zero():
    assert position_error(np.array([1.0, 2.0]), np.array([1.0, 2.0])) == 0.0


def test_position_error_known_case():
    assert math.isclose(position_error(np.array([3.0, 4.0]), np.array([0.0, 0.0])), 5.0)


def test_squared_error_is_position_error_squared():
    estimate = np.array([3.0, 4.0])
    truth = np.array([0.0, 0.0])
    assert math.isclose(squared_error(estimate, truth), position_error(estimate, truth) ** 2)


def test_mismatched_shapes_are_rejected():
    with pytest.raises(ValueError):
        position_error(np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0]))


def test_rmse_of_constant_errors_equals_that_constant():
    assert math.isclose(rmse([2.0, 2.0, 2.0]), 2.0)


def test_rmse_known_case():
    # errors 3 and 4: mean squared = (9 + 16) / 2 = 12.5, sqrt(12.5)
    assert math.isclose(rmse([3.0, 4.0]), math.sqrt(12.5))


def test_rmse_rejects_empty_list():
    with pytest.raises(ValueError):
        rmse([])
