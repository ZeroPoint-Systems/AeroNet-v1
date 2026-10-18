import numpy as np
import pytest

from simulation.estimation.covariance_intersection_core import (
    fuse_gaussians,
)


def test_equal_estimates_remain_equal():
    mean = np.array([1.0, -2.0])
    covariance = np.eye(2)

    fused_mean, fused_cov, weight = fuse_gaussians(
        mean, covariance, mean, covariance
    )

    np.testing.assert_allclose(fused_mean, mean)
    np.testing.assert_allclose(fused_cov, covariance)
    assert 0.0 <= weight <= 1.0


def test_fusion_returns_valid_covariance():
    mean_a = np.array([0.0, 1.0])
    mean_b = np.array([2.0, -1.0])
    covariance_a = np.array([[2.0, 0.2], [0.2, 1.0]])
    covariance_b = np.array([[1.0, 0.1], [0.1, 3.0]])

    mean, covariance, weight = fuse_gaussians(
        mean_a, covariance_a, mean_b, covariance_b
    )

    assert mean.shape == (2,)
    assert covariance.shape == (2, 2)
    assert np.all(np.isfinite(mean))
    assert np.allclose(covariance, covariance.T)
    assert np.linalg.eigvalsh(covariance).min() > 0
    assert 0.0 <= weight <= 1.0


def test_fixed_weight_is_respected():
    mean, covariance, weight = fuse_gaussians(
        [0.0], [[1.0]], [2.0], [[4.0]], weight=0.25
    )

    assert weight == 0.25
    assert mean.shape == (1,)
    assert covariance.shape == (1, 1)


@pytest.mark.parametrize("bad_weight", [-0.1, 1.1])
def test_invalid_weight_is_rejected(bad_weight):
    with pytest.raises(ValueError):
        fuse_gaussians([0.0], [[1.0]], [1.0], [[1.0]], weight=bad_weight)


def test_non_positive_definite_covariance_is_rejected():
    with pytest.raises(ValueError):
        fuse_gaussians([0.0, 0.0], [[1.0, 2.0], [2.0, 1.0]],
                       [1.0, 1.0], np.eye(2))


def test_incompatible_dimensions_are_rejected():
    with pytest.raises(ValueError):
        fuse_gaussians([0.0], [[1.0]], [0.0, 1.0], np.eye(2))


def test_logdet_objective_runs():
    mean, covariance, weight = fuse_gaussians(
        [0.0, 0.0], np.eye(2),
        [1.0, 1.0], 2.0 * np.eye(2),
        criterion="logdet",
    )

    assert np.all(np.isfinite(mean))
    assert np.linalg.eigvalsh(covariance).min() > 0
    assert 0.0 <= weight <= 1.0
