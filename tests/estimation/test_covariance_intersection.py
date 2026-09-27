import pytest

from simulation.estimation.covariance_intersection import CovarianceIntersectionEstimator


def test_construction_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        CovarianceIntersectionEstimator()
