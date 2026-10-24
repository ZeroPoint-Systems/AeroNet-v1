import numpy as np


def transition_matrix(dt):
    return np.array([[1, 0, dt, 0], [0, 1, 0, dt],
                     [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)


def process_covariance(dt, variance):
    q = float(variance)
    return q * np.array([
        [dt**4 / 4, 0, dt**3 / 2, 0],
        [0, dt**4 / 4, 0, dt**3 / 2],
        [dt**3 / 2, 0, dt**2, 0],
        [0, dt**3 / 2, 0, dt**2],
    ], dtype=float)


def measurement_matrix():
    return np.array([[1., 0., 0., 0.], [0., 1., 0., 0.]])


def simulate_truth(config, rng):
    f = transition_matrix(config.dt)
    q = process_covariance(config.dt, config.process_noise)
    chol = np.linalg.cholesky(q + np.eye(4) * 1e-12)
    truth = np.zeros((config.steps, 4), dtype=float)
    truth[0] = [0.0, 0.0, 0.45, 0.20]
    for t in range(1, config.steps):
        acceleration = np.array([0.035 * np.sin(t / 19.0),
                                 0.030 * np.cos(t / 23.0)])
        control = np.array([0.5 * config.dt**2 * acceleration[0],
                            0.5 * config.dt**2 * acceleration[1],
                            config.dt * acceleration[0],
                            config.dt * acceleration[1]])
        truth[t] = f @ truth[t - 1] + control + chol @ rng.normal(size=4)
    return truth
