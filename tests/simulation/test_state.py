import math

import numpy as np
import pytest

from simulation.core.state import State2D


def test_as_array_returns_x_then_y():
    s = State2D(1.0, 2.0)
    assert np.array_equal(s.as_array(), np.array([1.0, 2.0]))


def test_distance_between_zero_and_three_four_is_five():
    a = State2D(0.0, 0.0)
    b = State2D(3.0, 4.0)
    assert math.isclose(a.distance_to(b), 5.0)


def test_squared_distance_between_zero_and_three_four_is_twenty_five():
    a = State2D(0.0, 0.0)
    b = State2D(3.0, 4.0)
    assert math.isclose(a.squared_distance_to(b), 25.0)


def test_distance_is_symmetric():
    a = State2D(1.0, 2.0)
    b = State2D(-3.0, 5.0)
    assert math.isclose(a.distance_to(b), b.distance_to(a))


def test_nan_is_rejected():
    with pytest.raises(ValueError):
        State2D(float("nan"), 0.0)


def test_infinity_is_rejected():
    with pytest.raises(ValueError):
        State2D(0.0, float("inf"))


def test_state_is_immutable():
    s = State2D(1.0, 2.0)
    with pytest.raises(Exception):
        s.x = 5.0


def test_from_array_round_trips():
    original = State2D(3.5, -2.5)
    reconstructed = State2D.from_array(original.as_array())
    assert reconstructed == original
