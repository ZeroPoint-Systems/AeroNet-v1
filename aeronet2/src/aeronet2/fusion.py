"""Estimators.

InfoFilter  : exact fusion of *shared measurements* with arbitrary (bounded) delay and
              out-of-order arrival, via windowed retrodiction in information form.
              Each (origin, time) measurement is used at most once, so there is no
              double counting and no covariance-intersection conservatism.
CIFilter    : baseline that shares *estimates* and fuses with covariance intersection
              after propagating the stale peer estimate to the current time.
"""
from __future__ import annotations

import numpy as np

from .model import Scenario, H_POS, transition, process_cov, prior, sensor_R


def sym(P: np.ndarray) -> np.ndarray:
    return 0.5 * (P + P.T)


def predict_cov(P: np.ndarray, F: np.ndarray, Q: np.ndarray) -> np.ndarray:
    return sym(F @ P @ F.T + Q)


def meas_update_cov(P: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Posterior covariance after a position measurement with covariance R (Joseph-equivalent, stable)."""
    M = P[:, :2]
    S = P[:2, :2] + R
    return sym(P - M @ np.linalg.solve(S, M.T))


def pos_trace_gain(P: np.ndarray, R: np.ndarray) -> float:
    """Reduction in tr(position covariance) from fusing one position measurement of covariance R."""
    M = P[:, :2]
    S = P[:2, :2] + R
    G = M[:2] @ np.linalg.solve(S, M[:2].T)  # top-left 2x2 of M S^-1 M^T uses rows 0..1 of M
    # exact: tr of position block of (M S^-1 M^T) equals tr(M[:2] S^-1 M[:2]^T)
    return float(np.trace(G))


class InfoFilter:
    mode = "meas"

    def __init__(self, sc: Scenario, agent_id: int):
        self.sc, self.id = sc, agent_id
        self.F, self.Q = transition(sc), process_cov(sc)
        self.m0, self.P0 = prior(sc)
        self.Rs = sensor_R(sc)
        self.Rinv = [np.linalg.inv(R) for R in self.Rs]
        self.W = sc.window
        self.post: dict[int, tuple[np.ndarray, np.ndarray]] = {}
        self.contrib: dict[int, list] = {}
        self.seen: set[tuple[int, int]] = set()
        self.t = -1
        self.too_old = 0
        self.duplicates = 0
        self.last_innovation = 0.0

    # --- helpers -----------------------------------------------------------------
    def _add(self, origin: int, s: int, z: np.ndarray) -> None:
        Ri = self.Rinv[origin]
        c = self.contrib.setdefault(s, [np.zeros((4, 4)), np.zeros(4)])
        c[0][:2, :2] += Ri
        c[1][:2] += Ri @ z
        self.seen.add((origin, s))

    def _predict(self, k: int):
        if k == 0:
            return self.m0, self.P0
        x, P = self.post[k - 1]
        return self.F @ x, predict_cov(P, self.F, self.Q)

    def _recompute(self, k: int) -> None:
        xp, Pp = self._predict(k)
        c = self.contrib.get(k)
        if c is None:
            self.post[k] = (xp, Pp)
            return
        Pinv = np.linalg.inv(Pp)
        P = sym(np.linalg.inv(Pinv + c[0]))
        self.post[k] = (P @ (Pinv @ xp + c[1]), P)

    # --- interface -----------------------------------------------------------------
    def observe(self, t: int, z: np.ndarray) -> None:
        self.t = t
        xp, Pp = self._predict(t)
        nu = z - xp[:2]
        S = Pp[:2, :2] + self.Rs[self.id]
        self.last_innovation = float(np.sqrt(nu @ np.linalg.solve(S, nu)))
        self._add(self.id, t, z)
        self._recompute(t)
        old = t - self.W
        for k in [k for k in self.post if k < old]:
            del self.post[k]
        for k in [k for k in self.contrib if k < old]:
            del self.contrib[k]
        self.seen = {(o, s) for (o, s) in self.seen if s >= old}

    def receive(self, origin: int, s: int, z: np.ndarray, t_now: int) -> bool:
        if (origin, s) in self.seen:
            self.duplicates += 1
            return False
        if s < t_now - self.W + 1:
            self.too_old += 1
            return False
        self._add(origin, s, z)
        for k in range(s, t_now + 1):
            self._recompute(k)
        return True

    def estimate(self):
        return self.post[self.t]


class CIFilter:
    mode = "state"
    OMEGAS = np.linspace(0.0, 1.0, 21)

    def __init__(self, sc: Scenario, agent_id: int):
        self.sc, self.id = sc, agent_id
        self.F, self.Q = transition(sc), process_cov(sc)
        self.x, self.P = prior(sc)
        self.R = sensor_R(sc)[agent_id]
        self.t = -1
        self.last_innovation = 0.0

    def observe(self, t: int, z: np.ndarray) -> None:
        self.t = t
        if t > 0:
            self.x = self.F @ self.x
            self.P = predict_cov(self.P, self.F, self.Q)
        nu = z - self.x[:2]
        S = self.P[:2, :2] + self.R
        self.last_innovation = float(np.sqrt(nu @ np.linalg.solve(S, nu)))
        K = self.P[:, :2] @ np.linalg.inv(S)
        self.x = self.x + K @ nu
        IKH = np.eye(4) - K @ H_POS
        self.P = sym(IKH @ self.P @ IKH.T + K @ self.R @ K.T)  # Joseph form

    def receive_state(self, s: int, x: np.ndarray, P: np.ndarray, t_now: int) -> bool:
        xs, Ps = x.copy(), P.copy()
        for _ in range(t_now - s):
            xs = self.F @ xs
            Ps = predict_cov(Ps, self.F, self.Q)
        A, B = np.linalg.inv(self.P), np.linalg.inv(Ps)
        best = None
        for w in self.OMEGAS:
            Pf = np.linalg.inv(w * A + (1 - w) * B)
            tr = np.trace(Pf)
            if best is None or tr < best[0]:
                best = (tr, w, Pf)
        _, w, Pf = best
        self.x = Pf @ (w * A @ self.x + (1 - w) * B @ xs)
        self.P = sym(Pf)
        return True

    def estimate(self):
        return self.x, self.P
