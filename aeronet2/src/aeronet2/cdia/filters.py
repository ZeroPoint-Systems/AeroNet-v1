"""Information filter that also carries a second, finer sensing mode per agent."""
from __future__ import annotations

import numpy as np

from ..fusion import InfoFilter
from ..model import Scenario


class DualModeFilter(InfoFilter):
    """InfoFilter with origins 0..N-1 (nominal sensors) and N..2N-1 (fine mode, covariance R_i / kappa)."""

    def __init__(self, sc: Scenario, agent_id: int, kappa: float):
        super().__init__(sc, agent_id)
        self.n = sc.n_agents
        self.Rinv = self.Rinv + [kappa * Ri for Ri in self.Rinv]
        self.Rs = self.Rs + [R / kappa for R in self.Rs]

    def add_fine(self, t: int, z: np.ndarray) -> None:
        """Fuse this agent's own fine-mode measurement taken at step t (already observed this step)."""
        self._add(self.n + self.id, t, z)
        self._recompute(t)
