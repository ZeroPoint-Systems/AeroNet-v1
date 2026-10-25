"""Simulation loop, reference bounds and steady-state theory."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .fusion import CIFilter, InfoFilter, predict_cov, sym
from .model import (Scenario, H_POS, sensor_R, simulate_measurements, simulate_truth,
                    transition, process_cov, prior)
from .network import Network, Packet, packet_bytes
from .policies import AgentPolicy, ALL_POLICIES


@dataclass
class TrialResult:
    policy: str
    seed: int
    rmse_ss: float
    rmse_all: float
    nees_ss: float
    sent_per_agent: float
    bytes_sent: int
    delivered_frac: float
    accounting: dict
    too_old: int
    duplicates: int


def run_trial(sc: Scenario, policy: str, seed: int, truth=None, Z=None, keep_errors: bool = False):
    assert policy in ALL_POLICIES, policy
    if sc.window <= sc.delay_max + 1:
        raise ValueError("window must exceed delay_max + 1")
    truth = simulate_truth(sc, seed) if truth is None else truth
    Z = simulate_measurements(sc, truth, seed) if Z is None else Z
    net = Network(sc, seed)
    N, T = sc.n_agents, sc.steps
    use_ci = policy == "ci_periodic"
    flt = [CIFilter(sc, i) if use_ci else InfoFilter(sc, i) for i in range(N)]
    pol = [AgentPolicy(policy, sc, i, net.neighbours[i], seed, net.p_success) for i in range(N)]
    Rs = sensor_R(sc)
    err = np.zeros((T, N))
    nees = np.zeros((T, N))
    for t in range(T):
        for i in range(N):
            flt[i].observe(t, Z[t, i])
            pol[i].on_step(flt[i].last_innovation)
        for pkt in net.arrivals(t):
            j = pkt.dst
            if pkt.kind == "meas":
                flt[j].receive(pkt.src, pkt.t_send, pkt.z, t)
                pol[j].on_gossip(pkt.src, pkt.P, t - pkt.t_send)
            else:
                flt[j].receive_state(pkt.t_send, pkt.x, pkt.P, t)
        for i in range(N):
            for j in pol[i].decide(t, flt[i], bool(net.active[t, i])):
                x, P = flt[i].estimate()
                kind = flt[i].mode
                pkt = Packet(i, j, t, kind, z=Z[t, i].copy() if kind == "meas" else None,
                             x=x.copy() if kind == "state" else None, P=P.copy(), nbytes=packet_bytes(kind))
                net.transmit(t, pkt)
                pol[i].after_send(j, x[:2])
        for i in range(N):
            x, P = flt[i].estimate()
            e = x - truth[t]
            err[t, i] = np.linalg.norm(e[:2])
            nees[t, i] = float(e @ np.linalg.solve(P, e))
    net.finalize()
    a = net.acc
    assert a.consistent(), a
    s = slice(sc.burn_in, None)
    res = TrialResult(
        policy=policy, seed=seed,
        rmse_ss=float(np.sqrt(np.mean(err[s] ** 2))), rmse_all=float(np.sqrt(np.mean(err ** 2))),
        nees_ss=float(np.mean(nees[s])),
        sent_per_agent=a.sent / N, bytes_sent=a.bytes_sent,
        delivered_frac=(a.delivered / a.sent) if a.sent else float("nan"),
        accounting=dict(sent=a.sent, delivered=a.delivered, lost_channel=a.lost_channel,
                        lost_outage=a.lost_outage, lost_horizon=a.lost_horizon),
        too_old=sum(getattr(f, "too_old", 0) for f in flt),
        duplicates=sum(getattr(f, "duplicates", 0) for f in flt),
    )
    return (res, err, nees) if keep_errors else res


def centralised_rmse(sc: Scenario, seed: int, truth=None, Z=None) -> float:
    """KF fed every agent's measurement with no network (hard lower bound on achievable error)."""
    truth = simulate_truth(sc, seed) if truth is None else truth
    Z = simulate_measurements(sc, truth, seed) if Z is None else Z
    F, Q = transition(sc), process_cov(sc)
    Rinv = [np.linalg.inv(R) for R in sensor_R(sc)]
    Y = np.zeros((4, 4)); Y[:2, :2] = sum(Rinv)
    x, P = prior(sc)
    se = []
    for t in range(sc.steps):
        if t > 0:
            x, P = F @ x, predict_cov(P, F, Q)
        y = np.zeros(4); y[:2] = sum(Rinv[i] @ Z[t, i] for i in range(sc.n_agents))
        Pi = np.linalg.inv(P)
        P = sym(np.linalg.inv(Pi + Y))
        x = P @ (Pi @ x + y)
        if t >= sc.burn_in:
            se.append(np.sum((x[:2] - truth[t, :2]) ** 2))
    return float(np.sqrt(np.mean(se)))


def steady_state_pos_rmse(sc: Scenario, agents: list[int]) -> float:
    """Closed-form-by-iteration optimal steady-state position RMSE when `agents`' sensors are fused losslessly."""
    F, Q = transition(sc), process_cov(sc)
    Rs = sensor_R(sc)
    Y = np.zeros((4, 4))
    for i in agents:
        Y[:2, :2] += np.linalg.inv(Rs[i])
    _, P = prior(sc)
    for _ in range(2000):
        Pn = sym(np.linalg.inv(np.linalg.inv(predict_cov(P, F, Q)) + Y))
        if np.allclose(Pn, P, atol=1e-13):
            break
        P = Pn
    return float(np.sqrt(np.trace(P[:2, :2])))
