import numpy as np

from simulation.communication.channel import Channel
from simulation.communication.graph import CommunicationGraph
from simulation.communication.latency import FixedLatencyModel
from simulation.communication.packet_loss import PacketLossModel
from simulation.core.agent import Agent
from simulation.core.state import State2D
from simulation.estimation.reference_kalman import ReferenceKalmanFilter


def make_agent(agent_id: str, x: float, y: float) -> Agent:
    estimator = ReferenceKalmanFilter(
        initial_mean=np.zeros(2),
        initial_covariance=np.eye(2),
        process_noise_covariance=np.zeros((2, 2)),
    )
    return Agent(agent_id=agent_id, position=State2D(x, y), estimator=estimator)


def make_channel(loss_probability: float, latency: float, seed: int = 0) -> Channel:
    rng = np.random.default_rng(seed)
    return Channel(
        packet_loss_model=PacketLossModel(loss_probability=loss_probability, rng=rng),
        latency_model=FixedLatencyModel(latency=latency),
    )


def test_packet_is_never_delivered_before_scheduled_time():
    agents = [make_agent("a1", 0.0, 0.0), make_agent("a2", 1.0, 0.0)]
    graph = CommunicationGraph(agents, communication_range=10.0)
    channel = make_channel(loss_probability=0.0, latency=2.0)

    channel.send("a1", "a2", payload={"x": 1}, created_time=0.0, graph=graph)

    assert channel.collect_deliverable(current_time=1.0) == []
    delivered = channel.collect_deliverable(current_time=2.0)
    assert len(delivered) == 1
    assert delivered[0].sender_id == "a1"
    assert delivered[0].receiver_id == "a2"


def test_message_is_not_sent_across_a_missing_edge():
    agents = [make_agent("a1", 0.0, 0.0), make_agent("a2", 1000.0, 0.0)]
    graph = CommunicationGraph(agents, communication_range=10.0)
    channel = make_channel(loss_probability=0.0, latency=0.0)

    channel.send("a1", "a2", payload={"x": 1}, created_time=0.0, graph=graph)

    assert channel.pending_count() == 0
    assert channel.collect_deliverable(current_time=100.0) == []


def test_guaranteed_loss_never_delivers():
    agents = [make_agent("a1", 0.0, 0.0), make_agent("a2", 1.0, 0.0)]
    graph = CommunicationGraph(agents, communication_range=10.0)
    channel = make_channel(loss_probability=1.0, latency=0.0)

    channel.send("a1", "a2", payload={"x": 1}, created_time=0.0, graph=graph)

    assert channel.collect_deliverable(current_time=100.0) == []
    assert len(channel.lost_packets()) == 1
