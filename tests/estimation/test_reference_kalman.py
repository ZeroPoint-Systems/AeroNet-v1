import math

import numpy as np
import pytest

from simulation.estimation.reference_kalman import ReferenceKalmanFilter
from simulation.sensing.observation import Observation


def test_predict_adds_process_noise_scaled_by_dt():
    kf = ReferenceKalmanFilter(
        initial_mean=np.zeros(1),
        initial_covariance=np.array([[1.0]]),
        process_noise_covariance=np.array([[0.2]]),
    )
    kf.predict(dt=2.0)
    assert math.isclose(kf.covariance()[0, 0], 1.0 + 0.2 * 2.0)


def test_predict_does_not_change_mean_for_random_walk_model():
    kf = ReferenceKalmanFilter(
        initial_mean=np.array([3.0, -1.0]),
        initial_covariance=np.eye(2),
        process_noise_covariance=np.eye(2) * 0.1,
    )
    kf.predict(dt=1.0)
    assert np.allclose(kf.estimate(), np.array([3.0, -1.0]))


def test_single_update_matches_known_scalar_worked_example():
    # x0 = 0, P0 = 1, R = 1, z = 10
    # innovation covariance = P0 + R = 2
    # Kalman gain = P0 / (P0 + R) = 0.5
    # posterior mean = 0 + 0.5 * 10 = 5
    # posterior covariance = (1 - 0.5) * 1 = 0.5
    kf = ReferenceKalmanFilter(
        initial_mean=np.zeros(1),
        initial_covariance=np.array([[1.0]]),
        process_noise_covariance=np.array([[0.0]]),
    )
    observation = Observation(
        agent_id="a1", timestamp=0.0, value=np.array([10.0]), covariance=np.array([[1.0]])
    )
    kf.update(observation)
    assert math.isclose(kf.estimate()[0], 5.0)
    assert math.isclose(kf.covariance()[0, 0], 0.5)


def test_repeated_updates_converge_towards_true_value():
    rng = np.random.default_rng(0)
    true_value = 25.0
    kf = ReferenceKalmanFilter(
        initial_mean=np.zeros(1),
        initial_covariance=np.array([[100.0]]),
        process_noise_covariance=np.array([[0.0]]),
    )
    for t in range(500):
        noisy = true_value + rng.normal(0.0, 1.0)
        observation = Observation(
            agent_id="a1", timestamp=float(t), value=np.array([noisy]), covariance=np.array([[1.0]])
        )
        kf.update(observation)
    assert abs(kf.estimate()[0] - true_value) < 0.5
    assert kf.covariance()[0, 0] < 1.0


def test_covariance_shrinks_with_each_update():
    kf = ReferenceKalmanFilter(
        initial_mean=np.zeros(1),
        initial_covariance=np.array([[10.0]]),
        process_noise_covariance=np.array([[0.0]]),
    )
    previous_trace = kf.covariance()[0, 0]
    for t in range(5):
        observation = Observation(
            agent_id="a1", timestamp=float(t), value=np.array([1.0]), covariance=np.array([[1.0]])
        )
        kf.update(observation)
        current_trace = kf.covariance()[0, 0]
        assert current_trace < previous_trace
        previous_trace = current_trace


def test_incorporate_peer_estimate_is_not_implemented():
    kf = ReferenceKalmanFilter(
        initial_mean=np.zeros(2),
        initial_covariance=np.eye(2),
        process_noise_covariance=np.zeros((2, 2)),
    )
    with pytest.raises(NotImplementedError):
        kf.incorporate_peer_estimate("a2", np.zeros(2), np.eye(2))


def test_mismatched_covariance_shape_is_rejected():
    with pytest.raises(ValueError):
        ReferenceKalmanFilter(
            initial_mean=np.zeros(2),
            initial_covariance=np.eye(3),
            process_noise_covariance=np.eye(2),
        )
