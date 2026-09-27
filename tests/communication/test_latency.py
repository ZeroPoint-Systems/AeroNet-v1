import pytest

from simulation.communication.latency import FixedLatencyModel


def test_delivery_time_adds_fixed_latency():
    model = FixedLatencyModel(latency=2.5)
    assert model.delivery_time(created_time=10.0) == 12.5


def test_zero_latency_delivers_immediately():
    model = FixedLatencyModel(latency=0.0)
    assert model.delivery_time(created_time=3.0) == 3.0


def test_negative_latency_is_rejected():
    with pytest.raises(ValueError):
        FixedLatencyModel(latency=-1.0)
