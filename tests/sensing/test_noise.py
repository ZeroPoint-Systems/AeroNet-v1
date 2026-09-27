import numpy as np
import pytest

from simulation.sensing.noise import GaussianNoise


def test_zero_covariance_always_returns_zero():
    rng = np.random.default_rng(0)
    noise = GaussianNoise(covariance=np.zeros((2, 2)), rng=rng)
    for _ in range(5):
        assert np.allclose(noise.sample(), np.zeros(2))


def test_sample_shape_matches_covariance_dimension():
    rng = np.random.default_rng(0)
    noise = GaussianNoise(covariance=np.eye(3), rng=rng)
    sample = noise.sample()
    assert sample.shape == (3,)


def test_non_square_covariance_is_rejected():
    with pytest.raises(ValueError):
        GaussianNoise(covariance=np.ones((2, 3)), rng=np.random.default_rng(0))


def test_asymmetric_covariance_is_rejected():
    bad = np.array([[1.0, 0.5], [0.0, 1.0]])
    with pytest.raises(ValueError):
        GaussianNoise(covariance=bad, rng=np.random.default_rng(0))


def test_same_seed_gives_same_samples():
    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)
    noise_a = GaussianNoise(covariance=np.eye(2), rng=rng_a)
    noise_b = GaussianNoise(covariance=np.eye(2), rng=rng_b)
    assert np.allclose(noise_a.sample(), noise_b.sample())


def test_sample_mean_is_approximately_zero_over_many_draws():
    rng = np.random.default_rng(1)
    noise = GaussianNoise(covariance=np.eye(2) * 4.0, rng=rng)
    samples = np.array([noise.sample() for _ in range(20000)])
    assert np.allclose(samples.mean(axis=0), np.zeros(2), atol=0.1)
