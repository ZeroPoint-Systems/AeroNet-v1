import numpy as np

from simulation.communication.packet_loss import PacketLossModel


def test_zero_loss_probability_never_loses_a_packet():
    rng = np.random.default_rng(0)
    model = PacketLossModel(loss_probability=0.0, rng=rng)
    for _ in range(1000):
        assert model.is_lost() is False
    assert model.realised_loss_rate() == 0.0


def test_certain_loss_probability_always_loses_a_packet():
    rng = np.random.default_rng(0)
    model = PacketLossModel(loss_probability=1.0, rng=rng)
    for _ in range(1000):
        assert model.is_lost() is True
    assert model.realised_loss_rate() == 1.0


def test_realised_loss_rate_is_close_to_configured_probability():
    rng = np.random.default_rng(0)
    model = PacketLossModel(loss_probability=0.3, rng=rng)
    for _ in range(20000):
        model.is_lost()
    assert abs(model.realised_loss_rate() - 0.3) < 0.02
