"""Lossy, delayed, bursty-outage network with per-cause packet accounting.

All channel randomness is pre-drawn per (seed, step, src, dst), so every policy sees the
*same* network realisation for a given seed (common random numbers). A packet's fate
is therefore a function of the seed and of when/where it is sent, never of the policy's RNG.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .model import Scenario
from .rng import rng_for

GOSSIP_FLOATS = 10     # symmetric 4x4 covariance, upper triangle
HEADER_BYTES = 16      # src, dst, timestamp, kind


@dataclass
class Packet:
    src: int
    dst: int
    t_send: int
    kind: str                    # "meas" | "state"
    z: np.ndarray | None = None  # measurement (kind == "meas")
    x: np.ndarray | None = None  # state estimate (kind == "state")
    P: np.ndarray | None = None  # gossiped covariance (meas) or estimate covariance (state)
    nbytes: int = 0


def packet_bytes(kind: str, gossip: bool = True) -> int:
    n = HEADER_BYTES
    n += 8 * 2 if kind == "meas" else 8 * 4
    if gossip or kind == "state":
        n += 8 * GOSSIP_FLOATS
    return n


def adjacency(topology: str, n: int) -> list[list[int]]:
    if topology == "complete":
        return [[j for j in range(n) if j != i] for i in range(n)]
    if topology == "ring":
        return [sorted({(i - 1) % n, (i + 1) % n} - {i}) for i in range(n)]
    if topology == "line":
        return [[j for j in (i - 1, i + 1) if 0 <= j < n] for i in range(n)]
    raise ValueError(f"unknown topology {topology!r}")


@dataclass
class Accounting:
    sent: int = 0
    delivered: int = 0
    lost_channel: int = 0
    lost_outage: int = 0
    lost_horizon: int = 0
    bytes_sent: int = 0
    bytes_delivered: int = 0
    delays: list = field(default_factory=list)

    def consistent(self) -> bool:
        return self.sent == self.delivered + self.lost_channel + self.lost_outage + self.lost_horizon


class Network:
    def __init__(self, sc: Scenario, seed: int):
        self.sc = sc
        n, T = sc.n_agents, sc.steps
        self.neighbours = adjacency(sc.topology, n)
        lay = rng_for(seed, "layout")
        z = lay.standard_normal((n, n))
        self.link_loss = np.clip(sc.loss * np.exp(sc.link_loss_spread * z - 0.5 * sc.link_loss_spread**2), 0.0, 0.9)
        ch = rng_for(seed, "channel")
        self._u = ch.random((T, n, n))
        self._delay = ch.integers(sc.delay_min, sc.delay_max + 1, size=(T, n, n))
        self.active = np.ones((T, n), dtype=bool)
        if sc.outage_rate > 0:
            for i in range(n):
                r = rng_for(seed, "outage", i)
                t = 0
                while t < T:
                    if r.random() < sc.outage_rate:
                        d = int(r.integers(sc.outage_min, sc.outage_max + 1))
                        self.active[t : t + d, i] = False
                        t += d
                    else:
                        t += 1
        self.acc = Accounting()
        self._pending: dict[int, list[Packet]] = {}

    def p_success(self, i: int, j: int) -> float:
        """Nominal single-link delivery probability (what a deployed agent could estimate)."""
        return 1.0 - float(self.link_loss[i, j])

    def transmit(self, t: int, pkt: Packet) -> None:
        a = self.acc
        a.sent += 1
        a.bytes_sent += pkt.nbytes
        if self._u[t, pkt.src, pkt.dst] < self.link_loss[pkt.src, pkt.dst]:
            a.lost_channel += 1
            return
        arrive = t + int(self._delay[t, pkt.src, pkt.dst])
        if arrive >= self.sc.steps:
            a.lost_horizon += 1
            return
        self._pending.setdefault(arrive, []).append(pkt)

    def arrivals(self, t: int) -> list[Packet]:
        out = []
        for pkt in self._pending.pop(t, []):
            if self.active[t, pkt.dst]:
                self.acc.delivered += 1
                self.acc.bytes_delivered += pkt.nbytes
                self.acc.delays.append(t - pkt.t_send)
                out.append(pkt)
            else:
                self.acc.lost_outage += 1
        return out

    def finalize(self) -> None:
        for lst in self._pending.values():
            self.acc.lost_horizon += len(lst)
        self._pending.clear()
