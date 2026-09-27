"""Packet loss model.

The configured loss probability is a parameter of the model, not a
guarantee about what happens in any one run. This module also records how
many packets were actually generated, delivered and lost, so that the
realised loss rate can be checked against the configured probability
rather than assumed to match it.
"""

from __future__ import annotations

import numpy as np


class PacketLossModel:
    """Independent packet loss with a fixed probability per packet.

    ASSUMPTION: losses are independent across packets. A spatially or
    temporally correlated loss model is a distinct, explicitly separate
    adversarial condition, not the default.
    """

    def __init__(self, loss_probability: float, rng: np.random.Generator) -> None:
        if not (0.0 <= loss_probability <= 1.0):
            raise ValueError(f"loss_probability must be in [0, 1], got {loss_probability!r}")
        self.loss_probability = loss_probability
        self._rng = rng
        self.generated_count = 0
        self.delivered_count = 0
        self.lost_count = 0

    def is_lost(self) -> bool:
        """Decide, for one packet, whether it is lost. Updates the running
        generated/delivered/lost counters used to compute the realised loss
        rate.
        """
        self.generated_count += 1
        lost = self._rng.random() < self.loss_probability
        if lost:
            self.lost_count += 1
        else:
            self.delivered_count += 1
        return lost

    def realised_loss_rate(self) -> float:
        """The actual observed loss rate so far in this run, as distinct
        from the configured loss_probability.
        """
        if self.generated_count == 0:
            return 0.0
        return self.lost_count / self.generated_count
