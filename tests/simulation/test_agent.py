import numpy as np
import pytest

from simulation.core.agent import Agent
from simulation.core.state import State2D
from simulation.estimation.reference_kalman import ReferenceKalmanFilter
from simulation.sensing.observation import Observation


def make_agent(agent_id: str = "a1") -> Agent:
    estimator = ReferenceKalmanFilter(
        initial_mean=np.zeros(2),
        initial_covariance=np.eye(2) * 100.0,
        process_noise_covariance=np.zeros((2, 2)),
    )
    return Agent(agent_id=agent_id, position=State2D(0.0, 0.0), estimator=estimator)


def test_agent_rejects_empty_id():
    estimator = ReferenceKalmanFilter(
        initial_mean=np.zeros(2),
        initial_covariance=np.eye(2),
        process_noise_covariance=np.zeros((2, 2)),
    )
    with pytest.raises(ValueError):
        Agent(agent_id="", position=State2D(0.0, 0.0), estimator=estimator)


def test_agent_estimate_matches_estimator_output():
    agent = make_agent()
    assert np.array_equal(agent.estimate, np.zeros(2))


def test_agent_rejects_observation_addressed_to_another_agent():
    agent = make_agent("a1")
    observation = Observation(
        agent_id="a2",
        timestamp=0.0,
        value=np.array([1.0, 1.0]),
        covariance=np.eye(2),
    )
    with pytest.raises(ValueError):
        agent.receive_observation(observation)


def test_agent_update_moves_estimate_towards_observation():
    agent = make_agent("a1")
    observation = Observation(
        agent_id="a1",
        timestamp=0.0,
        value=np.array([10.0, 10.0]),
        covariance=np.eye(2),
    )
    agent.receive_observation(observation)
    # with an uninformative prior and a single observation, the posterior
    # mean should move a long way towards the observed value
    assert np.linalg.norm(agent.estimate - np.array([10.0, 10.0])) < 1.0


def test_agent_has_no_ground_truth_attribute():
    agent = make_agent()
    forbidden_names = {"true_state", "world", "ground_truth", "target"}
    assert forbidden_names.isdisjoint(vars(agent).keys())
