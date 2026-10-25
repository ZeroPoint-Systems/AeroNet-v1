"""Communication policies.

All scored policies share *one* budget-pacing mechanism (multiplicative quantile tracking),
so differences between them come only from the **score** that decides *when/where* to send.
This isolates the scientific question (is the score informative?) from threshold tuning.

  periodic     time-triggered schedule (deterministic, staggered offsets)
  random       score ~ U(0,1)                           (null-information control)
  innov        normalised innovation of own measurement (the v1 "reactive" signal)
  delta        |x_hat_pos - last_sent_pos|              (send-on-delta)
  voi_blind    expected position-trace reduction at a receiver *assumed* to share my covariance
  voi_open     expected reduction at each neighbour's *inferred* covariance, open loop (no feedback):
               data-independent, i.e. an offline greedy schedule
  voi_fb       voi_open + closed-loop feedback from gossiped covariances (peer-state-aware)
  voi_psa      NEW: voi_fb + consistency inflation (covariances scaled by the observed NIS excess so the
               score rises when the model is wrong) -- the proposed algorithm
  ci_periodic  estimate sharing + covariance intersection (classical baseline)
  broadcast    every agent sends to every neighbour every step (information upper reference)
  none         no communication
"""
from __future__ import annotations

import numpy as np

from .fusion import meas_update_cov, predict_cov, pos_trace_gain
from .model import Scenario, transition, process_cov, prior, sensor_R
from .rng import rng_for

SCORED = ("random", "innov", "delta", "voi_blind", "voi_open", "voi_fb", "voi_psa")
ALL_POLICIES = ("none", "periodic", "random", "innov", "delta", "voi_blind", "voi_open", "voi_fb", "voi_psa", "ci_periodic", "broadcast")


class Pacer:
    """Multiplicative quantile tracker (Robbins-Monro on log-threshold).

    Fires on a fraction ~ `rate` of eligible steps whatever the scale of the score. The gain decreases
    as 1/(1+n/n0) down to `gamma_min` so the threshold finds the right scale quickly (a fixed small
    gain was the cause of budget under-use in the first prototype) yet keeps tracking slow drift.
    """

    def __init__(self, rate: float, gamma0: float = 0.6, n0: float = 8.0, gamma_min: float = 0.03):
        self.rate, self.g0, self.n0, self.gmin = rate, gamma0, n0, gamma_min
        self.theta, self.n = None, 0

    def fire(self, score: float, rate: float | None = None) -> bool:
        rate = self.rate if rate is None else rate
        if self.theta is None:
            self.theta = max(score, 1e-9)
        fired = score > self.theta
        g = max(self.gmin, self.g0 / (1.0 + self.n / self.n0))
        self.theta *= float(np.exp(g * ((1.0 if fired else 0.0) - rate)))
        self.n += 1
        return fired


class PeerModel:
    """Agent i's belief about neighbour j's covariance: data-independent recursion using j's known sensor
    (sensor models are common knowledge), refreshed whenever a gossiped covariance from j arrives."""

    def __init__(self, sc: Scenario, me: int, neighbours: list[int]):
        self.F, self.Q = transition(sc), process_cov(sc)
        self.Rs = sensor_R(sc)
        _, P0 = prior(sc)
        self.P = {j: P0.copy() for j in neighbours}

    def step(self) -> None:
        for j in self.P:
            self.P[j] = meas_update_cov(predict_cov(self.P[j], self.F, self.Q), self.Rs[j])

    def refresh(self, j: int, P_gossip: np.ndarray, age: int) -> None:
        P = P_gossip
        for _ in range(age):
            P = meas_update_cov(predict_cov(P, self.F, self.Q), self.Rs[j])
        self.P[j] = P

    def after_send(self, j: int, R_sender: np.ndarray, p_success: float) -> None:
        P = self.P[j]
        self.P[j] = P + p_success * (meas_update_cov(P, R_sender) - P)  # expected covariance after (possibly lost) packet


class AgentPolicy:
    """Per-agent decision logic. `decide` returns a list of destinations (usually 0 or 1)."""

    def __init__(self, name: str, sc: Scenario, me: int, neighbours: list[int], seed: int, p_succ):
        self.name, self.sc, self.me, self.nb = name, sc, me, neighbours
        self.p_succ = p_succ
        self.sent = 0
        self.rr = 0
        self.rate = sc.budget / sc.steps
        self.pacer = Pacer(self.rate)
        self.rng = rng_for(seed, "policy", me)
        self.last_sent_pos = prior(sc)[0][:2].copy()
        self.peer = PeerModel(sc, me, neighbours) if name in ("voi_open", "voi_fb", "voi_psa") else None
        self.use_refresh = name in ("voi_fb", "voi_psa")
        self.use_inflation = name == "voi_psa"
        self.nis = 2.0   # EW mean of squared normalised innovation (2 dof => 2.0 when consistent)
        self.period = sc.steps / max(1, sc.budget)
        self.next_send = (me * self.period) / sc.n_agents
        self.Rs = sensor_R(sc)

    # round-robin receiver (used when the policy has no preference)
    def _rr(self) -> int:
        j = self.nb[self.rr % len(self.nb)]
        self.rr += 1
        return j

    def on_step(self, innovation: float = 0.0) -> None:
        self.nis += 0.15 * (innovation**2 - self.nis)
        if self.peer is not None:
            self.peer.step()

    def on_gossip(self, j: int, P: np.ndarray, age: int) -> None:
        if self.peer is not None and self.use_refresh and j in self.peer.P:
            self.peer.refresh(j, P, age)

    def decide(self, t: int, flt, active: bool) -> list[int]:
        n = self.name
        if n in ("none",):
            return []
        if n == "broadcast":
            return list(self.nb) if active else []
        if not active or self.sent >= self.sc.budget:
            return []
        if n in ("periodic", "ci_periodic"):
            if t >= self.next_send:
                self.next_send += self.period
                return [self._rr()]
            return []
        x, P = flt.estimate()
        Ri = self.Rs[self.me]
        left_steps = max(1, self.sc.steps - t)
        rate = min(1.0, max(0.0, (self.sc.budget - self.sent) / left_steps))
        infl = max(1.0, self.nis / 2.0) if self.use_inflation else 1.0
        if n == "random":
            return [self._rr()] if self.pacer.fire(float(self.rng.random()), rate) else []
        if n == "innov":
            return [self._rr()] if self.pacer.fire(flt.last_innovation, rate) else []
        if n == "delta":
            return [self._rr()] if self.pacer.fire(float(np.linalg.norm(x[:2] - self.last_sent_pos)), rate) else []
        if n == "voi_blind":
            best, bj = -1.0, None
            g = pos_trace_gain(P, Ri)
            for j in self.nb:
                v = self.p_succ(self.me, j) * g
                if v > best:
                    best, bj = v, j
            return [bj] if self.pacer.fire(best, rate) else []
        if n in ("voi_open", "voi_fb", "voi_psa"):
            best, bj = -1.0, None
            for j in self.nb:
                v = self.p_succ(self.me, j) * pos_trace_gain(infl * self.peer.P[j], Ri)
                if v > best:
                    best, bj = v, j
            return [bj] if self.pacer.fire(best, rate) else []
        raise ValueError(n)

    def after_send(self, j: int, x_pos: np.ndarray) -> None:
        self.sent += 1
        self.last_sent_pos = x_pos.copy()
        if self.peer is not None:
            self.peer.after_send(j, self.Rs[self.me], self.p_succ(self.me, j))
