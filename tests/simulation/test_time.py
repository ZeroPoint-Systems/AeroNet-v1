import math

import pytest

from simulation.core.time import SimulationClock


def test_starts_at_zero():
    clock = SimulationClock(dt=0.1)
    assert clock.time == 0.0
    assert clock.step_index == 0


def test_step_advances_time_by_dt():
    clock = SimulationClock(dt=0.5)
    clock.step()
    assert math.isclose(clock.time, 0.5)
    clock.step()
    assert math.isclose(clock.time, 1.0)


def test_invariant_time_equals_step_index_times_dt():
    clock = SimulationClock(dt=0.25)
    for _ in range(37):
        clock.step()
    assert math.isclose(clock.time, clock.step_index * clock.dt)


def test_reset_returns_to_zero():
    clock = SimulationClock(dt=0.1)
    for _ in range(10):
        clock.step()
    clock.reset()
    assert clock.time == 0.0
    assert clock.step_index == 0


def test_non_positive_dt_is_rejected():
    with pytest.raises(ValueError):
        SimulationClock(dt=0.0)
    with pytest.raises(ValueError):
        SimulationClock(dt=-1.0)


def test_negative_step_index_is_rejected():
    with pytest.raises(ValueError):
        SimulationClock(dt=0.1, step_index=-1)
