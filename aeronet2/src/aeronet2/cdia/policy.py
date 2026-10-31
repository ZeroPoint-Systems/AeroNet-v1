"""Per-agent resource allocation: sensing against communication under one budget.

Every agent holds a budget of `budget` units. One communication costs 1 unit, one fine-mode sensing action
costs `sense_cost` units. At each step the agent scores each affordable action by (utility gain) / (cost)
and takes the best one when the score exceeds an adaptive threshold that spreads the remaining budget over
the remaining steps (the same pacer as the other AeroNet2 policies).

Utilities
  decision : expected reduction in Bayes decision error (CDIA)
  trace    : reduction in the trace of the position covariance (information-theoretic reference)

The value of a transmission is evaluated for the receiver's inferred covariance (PeerModel, refreshed by
gossiped covariances), the sender's own estimate standing in for the receiver's mean, and a measurement
noise inflated for the expected delivery delay.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..fusion import pos_trace_gain
from ..model import Scenario, process_cov, sensor_R, transition
from ..policies import Pacer, PeerModel
from .decision import age_inflated_noise, measurement_value

FAMILY = {
    "cdia": ("decision", True),
    "cdia_comm": ("decision", False),
    "trace_joint": ("trace", True),
    "trace_comm": ("trace", False),
}


@dataclass
class Action:
    kind: str                 # "idle" | "sense" | "send"
    dst: int = -1
    score: float = 0.0


class AllocationPolicy:
    def __init__(self, name: str, sc: Scenario, me: int, neighbours: list[int], p_succ,
                 c4: np.ndarray, tau: float, kappa: float, sense_cost: float):
        self.utility, self.can_sense = FAMILY[name]
        self.sc, self.me, self.nb, self.p_succ = sc, me, neighbours, p_succ
        self.c4, self.tau, self.kappa, self.sense_cost = c4, tau, kappa, sense_cost
        self.units = 0.0
        self.pacer = Pacer(sc.budget / sc.steps)
        self.peer = PeerModel(sc, me, neighbours)
        self.Rs = sensor_R(sc)
        F, Q = transition(sc), process_cov(sc)
        mean_delay = int(round(0.5 * (sc.delay_min + sc.delay_max)))
        self.F, self.Q, self.mean_delay = F, Q, mean_delay
        self.R_air = age_inflated_noise(self.Rs[me], F, Q, mean_delay)
        self.R_fine = self.Rs[me] / kappa
        self.max_age = sc.window - 1 - sc.delay_max
        self.pending_t: int | None = None     # time of the latest unsent fine measurement

    def on_step(self) -> None:
        self.peer.step()

    def on_gossip(self, j: int, P: np.ndarray, age: int) -> None:
        if j in self.peer.P:
            self.peer.refresh(j, P, age)

    def note_sensed(self, t: int) -> None:
        self.pending_t = t

    def send_fine_at(self, t: int) -> int | None:
        """Time of the fine measurement a transmission at step t would carry, or None for the nominal one."""
        if self.pending_t is not None and t - self.pending_t <= self.max_age:
            return self.pending_t
        return None

    def _send_noise(self, t: int) -> np.ndarray:
        ts = self.send_fine_at(t)
        if ts is None:
            return self.R_air
        return age_inflated_noise(self.R_fine, self.F, self.Q, t - ts + self.mean_delay)

    def _gain(self, P: np.ndarray, R: np.ndarray, x: np.ndarray) -> float:
        if self.utility == "trace":
            return pos_trace_gain(P, R)
        return measurement_value(P, R, self.c4, float(self.c4 @ x - self.tau))

    def decide(self, t: int, flt, radio_up: bool) -> Action:
        sc = self.sc
        left = max(1, sc.steps - t)
        remaining = sc.budget - self.units
        if remaining < 1.0 and not (self.can_sense and remaining >= self.sense_cost):
            return Action("idle")
        x, P = flt.estimate()
        best = Action("idle", score=-1.0)
        if radio_up and remaining >= 1.0:
            R_send = self._send_noise(t)
            for j in self.nb:
                s = self.p_succ(self.me, j) * self._gain(self.peer.P[j], R_send, x)
                if s > best.score:
                    best = Action("send", j, s)
        if self.can_sense and remaining >= self.sense_cost:
            s = self._gain(P, self.R_fine, x) / self.sense_cost
            if s > best.score:
                best = Action("sense", -1, s)
        if best.kind == "idle":
            return best
        rate = min(1.0, max(0.0, remaining / left))
        return best if self.pacer.fire(best.score, rate) else Action("idle")

    def commit(self, action: Action, t: int) -> None:
        if action.kind == "send":
            self.units += 1.0
            fine = self.send_fine_at(t) is not None
            self.peer.after_send(action.dst, self.R_fine if fine else self.Rs[self.me], self.p_succ(self.me, action.dst))
            if fine:
                self.pending_t = None
        elif action.kind == "sense":
            self.units += self.sense_cost
            self.note_sensed(t)


class SplitPeriodic:
    """Budget split between periodic communication and periodic fine sensing (no adaptation)."""

    def __init__(self, sc: Scenario, me: int, neighbours: list[int], sense_cost: float, comm_share: float = 0.5):
        self.sc, self.me, self.nb = sc, me, neighbours
        n_comm = int(round(comm_share * sc.budget))
        n_sense = int((sc.budget - n_comm) / sense_cost)
        self.units, self.rr = 0.0, 0
        self.sense_cost = sense_cost
        self.p_comm = sc.steps / max(1, n_comm)
        self.p_sense = sc.steps / max(1, n_sense)
        self.next_comm = me * self.p_comm / sc.n_agents
        self.next_sense = me * self.p_sense / sc.n_agents + 0.5 * self.p_sense
        self.n_comm, self.n_sense, self.sent, self.sensed = n_comm, n_sense, 0, 0
        self.pending_t: int | None = None
        self.max_age = sc.window - 1 - sc.delay_max

    def send_fine_at(self, t: int) -> int | None:
        if self.pending_t is not None and t - self.pending_t <= self.max_age:
            return self.pending_t
        return None

    def on_step(self) -> None: ...

    def on_gossip(self, j, P, age) -> None: ...

    def decide(self, t: int, flt, radio_up: bool) -> Action:
        if self.sensed < self.n_sense and t >= self.next_sense:
            self.next_sense += self.p_sense
            return Action("sense")
        if radio_up and self.sent < self.n_comm and t >= self.next_comm:
            self.next_comm += self.p_comm
            j = self.nb[self.rr % len(self.nb)]
            self.rr += 1
            return Action("send", j)
        return Action("idle")

    def commit(self, action: Action, t: int) -> None:
        if action.kind == "send":
            self.sent += 1
            self.units += 1.0
            if self.send_fine_at(t) is not None:
                self.pending_t = None
        elif action.kind == "sense":
            self.sensed += 1
            self.units += self.sense_cost
            self.pending_t = t


class OracleBoundary:
    """Unattainable reference: uses the true target position to act only while the decision is contested.

    Acts (send or sense) on every k-th contested step, with k chosen from the total number of contested
    steps so that the budget is spread over them. Needs hindsight, so it is a bound, not a competitor.
    """

    def __init__(self, mode: str, sc: Scenario, me: int, neighbours: list[int], truth: np.ndarray,
                 c4: np.ndarray, tau: float, width: float, sense_cost: float):
        self.mode, self.sc, self.me, self.nb, self.sense_cost = mode, sc, me, neighbours, sense_cost
        margin = np.abs(truth[:, :2] @ c4[:2] - tau)
        self.zone = margin < width
        n_actions = int(sc.budget / (sense_cost if mode == "sense" else 1.0))
        self.k = max(1, int(np.ceil(self.zone.sum() / max(1, n_actions))))
        self.count, self.units, self.rr = 0, 0.0, 0
        self.pending_t: int | None = None
        self.max_age = sc.window - 1 - sc.delay_max

    def on_step(self) -> None: ...

    def on_gossip(self, j, P, age) -> None: ...

    def send_fine_at(self, t: int) -> int | None:
        if self.pending_t is not None and t - self.pending_t <= self.max_age:
            return self.pending_t
        return None

    def decide(self, t: int, flt, radio_up: bool) -> Action:
        if not self.zone[t]:
            return Action("idle")
        self.count += 1
        if (self.count - 1) % self.k:
            return Action("idle")
        if self.mode == "sense":
            return Action("sense") if self.units + self.sense_cost <= self.sc.budget else Action("idle")
        if radio_up and self.units + 1.0 <= self.sc.budget:
            j = self.nb[self.rr % len(self.nb)]
            self.rr += 1
            return Action("send", j)
        return Action("idle")

    def commit(self, action: Action, t: int) -> None:
        self.units += self.sense_cost if action.kind == "sense" else 1.0
        if action.kind == "sense":
            self.pending_t = t
        elif self.send_fine_at(t) is not None:
            self.pending_t = None
