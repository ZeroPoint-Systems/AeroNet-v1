import numpy as np
from aeronet.config import ExperimentConfig
from aeronet.model import measurement_matrix, simulate_truth, transition_matrix


def test_transition_and_measurement_shapes():
    assert transition_matrix(1.0).shape == (4, 4)
    h = measurement_matrix()
    assert h.shape == (2, 4)
    assert np.allclose(h[:, :2], np.eye(2))
    assert np.allclose(h[:, 2:], 0)


def test_truth_reproducible():
    c = ExperimentConfig(steps=30)
    assert np.allclose(simulate_truth(c, np.random.default_rng(12)),
                       simulate_truth(c, np.random.default_rng(12)))


def test_invalid_configuration_rejected():
    try:
        ExperimentConfig(dt=0).validate()
    except ValueError:
        return
    raise AssertionError("invalid dt was accepted")
