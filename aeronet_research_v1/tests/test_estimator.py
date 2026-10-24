import numpy as np
from aeronet.estimator import LocalKalmanFilter


def test_filter_finite_symmetric_psd():
    f = LocalKalmanFilter(1.0, 0.04, 0.3)
    for _ in range(30):
        f.predict()
        f.update(np.array([0.1, -0.2]))
    assert np.isfinite(f.x).all()
    assert np.isfinite(f.P).all()
    assert np.allclose(f.P, f.P.T, atol=1e-9)
    assert np.linalg.eigvalsh(f.P).min() > -1e-8


def test_consensus_does_not_shrink_covariance():
    f = LocalKalmanFilter(1.0, 0.04, 0.3)
    before = f.P.copy()
    f.consensus([np.ones(4) * 100])
    assert np.allclose(f.P, before)
    assert np.max(np.abs(f.x)) <= 0.16
