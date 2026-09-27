import numpy as np
import pytest

from simulation.core.state import State2D
from simulation.sensing.observation_model import DirectGaussianObservationModel


def test_observation_is_centred_on_true_state_over_many_draws():
    rng = np.random.default_rng(0)
    model = DirectGaussianObservationModel(measurement_covariance=np.eye(2) * 1.0, rng=rng)
    truth = State2D(50.0, 50.0)
    values = []
    for _ in range(5000):
        obs = model.observe(
            agent_id="a1",
            agent_position=State2D(0.0, 0.0),
            true_state=truth,
            timestamp=0.0,
        )
        values.append(obs.value)
    mean_value = np.mean(values, axis=0)
    assert np.allclose(mean_value, truth.as_array(), atol=0.2)


def test_observation_carries_correct_agent_id_and_timestamp():
    rng = np.random.default_rng(0)
    model = DirectGaussianObservationModel(measurement_covariance=np.eye(2), rng=rng)
    obs = model.observe(
        agent_id="a7",
        agent_position=State2D(0.0, 0.0),
        true_state=State2D(1.0, 1.0),
        timestamp=3.5,
    )
    assert obs.agent_id == "a7"
    assert obs.timestamp == 3.5


def test_zero_noise_observation_equals_truth_exactly():
    rng = np.random.default_rng(0)
    model = DirectGaussianObservationModel(measurement_covariance=np.zeros((2, 2)), rng=rng)
    truth = State2D(12.0, -7.0)
    obs = model.observe(agent_id="a1", agent_position=State2D(0.0, 0.0), true_state=truth, timestamp=0.0)
    assert np.allclose(obs.value, truth.as_array())
