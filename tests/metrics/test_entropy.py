import math

import numpy as np
import pytest

from analysis.metrics.entropy import gaussian_entropy


def test_entropy_of_identity_covariance_in_two_dimensions():
    # H = 0.5 * (2 * log(2*pi*e) + log(1)) = log(2*pi*e)
    expected = math.log(2 * math.pi * math.e)
    assert math.isclose(gaussian_entropy(np.eye(2)), expected)


def test_larger_covariance_gives_larger_entropy():
    small = gaussian_entropy(np.eye(2) * 1.0)
    large = gaussian_entropy(np.eye(2) * 10.0)
    assert large > small


def test_non_positive_definite_covariance_is_rejected():
    with pytest.raises(ValueError):
        gaussian_entropy(np.zeros((2, 2)))
