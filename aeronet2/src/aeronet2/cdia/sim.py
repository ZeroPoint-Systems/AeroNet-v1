"""Trial runner for the sensing-and-communication allocation experiments."""
from __future__ import annotations

import time
from dataclasses import dataclass, asdict, field

import numpy as np

from ..model import Scenario, sensor_R, simulate_measurements, simulate_truth
from ..network import Network, Packet, packet_bytes
from ..policies import AgentPolicy
from ..rng import rng_for
from .filters import DualModeFilter
from .policy import FAMILY, Action, AllocationPolicy, OracleBoundary, SplitPeriodic

LEGACY = {"none": "none", "periodic_comm": "periodic", "innov_comm": "innov", "broadcast": "broadcast"}
ORACLES = ("oracle_send", "oracle_sense")      # hindsight references, never competitors
POLICIES = tuple(LEGACY) + ("periodic_split",) + tuple(FAMILY) + ORACLES


@dataclass(frozen=True)
class Decision:
    """Team decision: sign of c.pos - tau, with c a unit vector in the plane."""
    angle: float = 0.0
    tau: float = 0.0

    def c4(self) -> np.ndarray:
        return np.array([np.cos(self.angle), np.sin(self.angle), 0.0, 0.0])


@dataclass
class CdiaResult:
    policy: str
    seed: int
    decision_error: float
    rmse_ss: float
    units_per_agent: float
    sent_per_agent: float
    sensed_per_agent: float
    bytes_sent: int
    delivered_frac: float
    policy_seconds: float
    decisions_evaluated: int
    too_old: int
    duplicates: int


def run_trial(sc: Scenario, policy: str, seed: int, dec: Decision, kappa: float = 4.0, sense_cost: float = 1.0,
              truth=None, Z=None) -> CdiaResult:
    if policy not in POLICIES:
        raise ValueError(policy)
    if sc.window <= sc.delay_max + 1:
        raise ValueError("window must exceed delay_max + 1")
    truth = simulate_truth(sc, seed) if truth is None else truth
    Z = simulate_measurements(sc, truth, seed) if Z is None else Z
    N, T = sc.n_agents, sc.steps
    Rs = sensor_R(sc)
    fine_rng = [rng_for(seed, "sensor", N + i) for i in range(N)]
    Zf = np.empty((T, N, 2))
    for i in range(N):
        L = np.linalg.cholesky(Rs[i] / kappa)
        Zf[:, i, :] = truth[:, :2] + fine_rng[i].standard_normal((T, 2)) @ L.T
    net = Network(sc, seed)
    flt = [DualModeFilter(sc, i, kappa) for i in range(N)]
    c4 = dec.c4()
    if policy in LEGACY:
        pol = [AgentPolicy(LEGACY[policy], sc, i, net.neighbours[i], seed, net.p_success) for i in range(N)]
    elif policy in ORACLES:
        pol = [OracleBoundary(policy.split("_")[1], sc, i, net.neighbours[i], truth, c4, dec.tau, 2.0, sense_cost)
               for i in range(N)]
    elif policy == "periodic_split":
        pol = [SplitPeriodic(sc, i, net.neighbours[i], sense_cost) for i in range(N)]
    else:
        pol = [AllocationPolicy(policy, sc, i, net.neighbours[i], net.p_success, c4, dec.tau, kappa, sense_cost)
               for i in range(N)]
    legacy = policy in LEGACY
    fine_store: list[dict[int, np.ndarray]] = [dict() for _ in range(N)]
    sensed = np.zeros(N)
    est_pos = np.zeros((T, N, 2))
    err2 = np.zeros((T, N))
    policy_time = 0.0
    for t in range(T):
        for i in range(N):
            flt[i].observe(t, Z[t, i])
            if legacy:
                pol[i].on_step(flt[i].last_innovation)
            else:
                pol[i].on_step()
        for pkt in net.arrivals(t):
            j = pkt.dst
            origin = pkt.src + (N if pkt.origin_fine else 0)
            flt[j].receive(origin, pkt.t_send_meas, pkt.z, t)
            pol[j].on_gossip(pkt.src, pkt.P, t - pkt.t_send)
        for i in range(N):
            t0 = time.perf_counter()
            if legacy:
                dests = pol[i].decide(t, flt[i], bool(net.active[t, i]))
                acts = [Action("send", j) for j in dests]
            else:
                acts = [pol[i].decide(t, flt[i], bool(net.active[t, i]))]
            policy_time += time.perf_counter() - t0
            for a in acts:
                if a.kind == "sense":
                    flt[i].add_fine(t, Zf[t, i])
                    fine_store[i][t] = Zf[t, i].copy()
                    sensed[i] += 1
                    pol[i].commit(a, t)
                elif a.kind == "send":
                    ts = None if legacy else pol[i].send_fine_at(t)
                    fine = ts is not None
                    z = fine_store[i][ts] if fine else Z[t, i]
                    x, P = flt[i].estimate()
                    pkt = SensePacket(i, a.dst, t, "meas", z=z.copy(), P=P.copy(), nbytes=packet_bytes("meas"),
                                      origin_fine=fine, t_send_meas=ts if fine else t)
                    net.transmit(t, pkt)
                    if legacy:
                        pol[i].after_send(a.dst, x[:2])
                    else:
                        pol[i].commit(a, t)
        for i in range(N):
            x, _ = flt[i].estimate()
            est_pos[t, i] = x[:2]
            err2[t, i] = np.sum((x[:2] - truth[t, :2]) ** 2)
    net.finalize()
    assert net.acc.consistent()
    s = slice(sc.burn_in, None)
    y = (truth[s, :2] @ c4[:2]) > dec.tau
    a = (est_pos[s] @ c4[:2]) > dec.tau
    wrong = a != y[:, None]
    units = (net.acc.sent + sense_cost * sensed.sum()) / N
    return CdiaResult(policy=policy, seed=seed, decision_error=float(wrong.mean()),
                      rmse_ss=float(np.sqrt(np.mean(err2[s]))), units_per_agent=float(units),
                      sent_per_agent=net.acc.sent / N, sensed_per_agent=float(sensed.mean()),
                      bytes_sent=net.acc.bytes_sent,
                      delivered_frac=(net.acc.delivered / net.acc.sent) if net.acc.sent else float("nan"),
                      policy_seconds=policy_time, decisions_evaluated=T * N,
                      too_old=sum(f.too_old for f in flt), duplicates=sum(f.duplicates for f in flt))


@dataclass
class SensePacket(Packet):
    origin_fine: bool = False
    t_send_meas: int = 0
