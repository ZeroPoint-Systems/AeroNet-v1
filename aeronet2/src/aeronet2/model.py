"""Target dynamics, sensor models and scenario configuration."""
from __future__ import annotations

from dataclasses import dataclass, replace, asdict

import numpy as np

from .rng import rng_for


@dataclass(frozen=True)
class Scenario:
    # --- horizon / agents
    n_agents: int = 6
    steps: int = 240
    burn_in: int = 40
    dt: float = 1.0
    # --- target (continuous white-noise-acceleration constant-velocity model)
    q: float = 0.05
    prior_pos_var: float = 4.0
    prior_vel_var: float = 1.0
    manoeuvre_rate: float = 0.0    # per-step probability a manoeuvre burst starts (unmodelled by the filters)
    manoeuvre_acc: float = 0.6     # burst acceleration magnitude
    manoeuvre_len: int = 12        # burst duration (steps)
    # --- sensing: R_i has constant determinant sigma^4, anisotropy only changes its *shape*
    sigma: float = 0.6
    anisotropy: float = 1.0        # sigma_perp / sigma_par ; 1.0 == homogeneous isotropic
    sensor_spread: float = 0.0     # log-spread of per-agent sensor quality
    # --- network
    topology: str = "ring"         # ring | complete | line
    loss: float = 0.10
    link_loss_spread: float = 0.0  # lognormal spread of per-link loss
    delay_min: int = 1
    delay_max: int = 3
    outage_rate: float = 0.0       # per-step probability an agent's radio goes down
    outage_min: int = 3
    outage_max: int = 10
    # --- communication budget (packets per agent over the horizon)
    budget: int = 30
    window: int = 12               # retrodiction window (must exceed max delay + 1)

    def replace(self, **kw) -> "Scenario":
        return replace(self, **kw)

    def as_dict(self) -> dict:
        return asdict(self)


def transition(sc: Scenario) -> np.ndarray:
    I2 = np.eye(2)
    F = np.eye(4)
    F[:2, 2:] = sc.dt * I2
    return F


def process_cov(sc: Scenario) -> np.ndarray:
    dt, q = sc.dt, sc.q
    I2 = np.eye(2)
    return q * np.block([[dt**3 / 3 * I2, dt**2 / 2 * I2], [dt**2 / 2 * I2, dt * I2]])


def prior(sc: Scenario) -> tuple[np.ndarray, np.ndarray]:
    return np.zeros(4), np.diag([sc.prior_pos_var] * 2 + [sc.prior_vel_var] * 2)


H_POS = np.hstack([np.eye(2), np.zeros((2, 2))])


def sensor_R(sc: Scenario) -> list[np.ndarray]:
    """Per-agent measurement covariance (2x2). Directions are spread over a half circle."""
    n = sc.n_agents
    out = []
    spread = np.linspace(-1.0, 1.0, n) if n > 1 else np.zeros(1)
    for i in range(n):
        th = np.pi * i / n
        U = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        rho = sc.anisotropy
        s = sc.sigma * np.exp(sc.sensor_spread * spread[i])
        s_par, s_perp = s / np.sqrt(rho), s * np.sqrt(rho)   # det = s^4 for every rho
        out.append(U @ np.diag([s_par**2, s_perp**2]) @ U.T)
    return out


def simulate_truth(sc: Scenario, seed: int) -> np.ndarray:
    rng = rng_for(seed, "truth")
    F, Q = transition(sc), process_cov(sc)
    m0, P0 = prior(sc)
    L = np.linalg.cholesky(Q)
    B = np.vstack([0.5 * sc.dt**2 * np.eye(2), sc.dt * np.eye(2)])
    x = m0 + np.linalg.cholesky(P0) @ rng.standard_normal(4)
    out = np.empty((sc.steps, 4))
    left, acc = 0, np.zeros(2)
    for t in range(sc.steps):
        if t > 0:
            x = F @ x + L @ rng.standard_normal(4)
            if sc.manoeuvre_rate > 0:
                if left == 0 and rng.random() < sc.manoeuvre_rate:
                    th = rng.uniform(0, 2 * np.pi)
                    acc, left = sc.manoeuvre_acc * np.array([np.cos(th), np.sin(th)]), sc.manoeuvre_len
                if left > 0:
                    x = x + B @ acc
                    left -= 1
        out[t] = x
    return out


def simulate_measurements(sc: Scenario, truth: np.ndarray, seed: int) -> np.ndarray:
    """Z[t, i, :] : common random numbers across policies for a given seed."""
    Rs = sensor_R(sc)
    Z = np.empty((sc.steps, sc.n_agents, 2))
    for i in range(sc.n_agents):
        rng = rng_for(seed, "sensor", i)
        L = np.linalg.cholesky(Rs[i])
        noise = rng.standard_normal((sc.steps, 2)) @ L.T
        Z[:, i, :] = truth[:, :2] + noise
    return Z
