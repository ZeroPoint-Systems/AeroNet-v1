import numpy as np
import pytest

from simulation.core.agent import Agent
from simulation.core.state import State2D
from simulation.core.swarm import DuplicateAgentIDError, Swarm, UnknownAgentIDError
from simulation.estimation.reference_kalman import ReferenceKalmanFilter


def make_agent(agent_id: str, available: bool = True) -> Agent:
    estimator = ReferenceKalmanFilter(
        initial_mean=np.zeros(2),
        initial_covariance=np.eye(2) * 100.0,
        process_noise_covariance=np.zeros((2, 2)),
    )
    return Agent(agent_id=agent_id, position=State2D(0.0, 0.0), estimator=estimator, available=available)


def test_add_and_get_agent():
    swarm = Swarm()
    agent = make_agent("a1")
    swarm.add_agent(agent)
    assert swarm.get_agent("a1") is agent


def test_duplicate_agent_id_is_rejected():
    swarm = Swarm()
    swarm.add_agent(make_agent("a1"))
    with pytest.raises(DuplicateAgentIDError):
        swarm.add_agent(make_agent("a1"))


def test_unknown_agent_id_raises_on_get_and_remove():
    swarm = Swarm()
    with pytest.raises(UnknownAgentIDError):
        swarm.get_agent("does-not-exist")
    with pytest.raises(UnknownAgentIDError):
        swarm.remove_agent("does-not-exist")


def test_remove_agent():
    swarm = Swarm()
    swarm.add_agent(make_agent("a1"))
    swarm.remove_agent("a1")
    assert swarm.agent_count() == 0


def test_agent_count_available_and_failed():
    swarm = Swarm()
    swarm.add_agent(make_agent("a1", available=True))
    swarm.add_agent(make_agent("a2", available=True))
    swarm.add_agent(make_agent("a3", available=False))

    assert swarm.agent_count() == 3
    assert swarm.available_agent_count() == 2
    assert swarm.failed_agent_count() == 1
    assert {a.agent_id for a in swarm.active_agents()} == {"a1", "a2"}


def test_swarm_is_iterable_and_has_len():
    swarm = Swarm()
    swarm.add_agent(make_agent("a1"))
    swarm.add_agent(make_agent("a2"))
    assert len(swarm) == 2
    assert {a.agent_id for a in swarm} == {"a1", "a2"}
