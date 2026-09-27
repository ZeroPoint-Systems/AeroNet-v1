import numpy as np

from simulation.communication.graph import CommunicationGraph
from simulation.core.agent import Agent
from simulation.core.state import State2D
from simulation.estimation.reference_kalman import ReferenceKalmanFilter


def make_agent(agent_id: str, x: float, y: float, available: bool = True) -> Agent:
    estimator = ReferenceKalmanFilter(
        initial_mean=np.zeros(2),
        initial_covariance=np.eye(2),
        process_noise_covariance=np.zeros((2, 2)),
    )
    return Agent(agent_id=agent_id, position=State2D(x, y), estimator=estimator, available=available)


def test_agents_within_range_are_connected():
    agents = [make_agent("a1", 0.0, 0.0), make_agent("a2", 5.0, 0.0)]
    graph = CommunicationGraph(agents, communication_range=10.0)
    assert graph.has_edge("a1", "a2")
    assert graph.neighbours("a1") == {"a2"}


def test_agents_outside_range_are_not_connected():
    agents = [make_agent("a1", 0.0, 0.0), make_agent("a2", 100.0, 0.0)]
    graph = CommunicationGraph(agents, communication_range=10.0)
    assert not graph.has_edge("a1", "a2")
    assert graph.neighbours("a1") == set()


def test_unavailable_agents_have_no_edges():
    agents = [make_agent("a1", 0.0, 0.0), make_agent("a2", 1.0, 0.0, available=False)]
    graph = CommunicationGraph(agents, communication_range=10.0)
    assert graph.neighbours("a1") == set()
    assert graph.neighbours("a2") == set()


def test_edge_count_for_fully_connected_triangle():
    agents = [make_agent("a1", 0.0, 0.0), make_agent("a2", 1.0, 0.0), make_agent("a3", 0.0, 1.0)]
    graph = CommunicationGraph(agents, communication_range=10.0)
    assert graph.edge_count() == 3
