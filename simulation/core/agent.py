"""Agent abstraction.

An agent is deliberately narrow. It knows its own identity, its own
position, its own availability, and holds an estimator that produces its
local estimate and local uncertainty. It has no attribute, method, or
reference of any kind that exposes the true state of the world.

The only two ways an agent can learn anything about the world are:

  1. through an Observation passed to it by the sensing layer
  2. through a peer estimate passed to it by the communication layer

Anything that bypasses those two paths, such as an agent holding a direct
reference to the World or to another agent, is a scientific validity bug,
not a convenience shortcut. See tests/reproducibility/test_information_isolation.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from simulation.core.state import State2D

if TYPE_CHECKING:
    from simulation.estimation.base import Estimator
    from simulation.sensing.observation import Observation


class Agent:
    """A single decentralised agent.

    Parameters
    ----------
    agent_id:
        A unique, stable identifier for this agent.
    position:
        The agent's own position. In the sprint 1 configuration this is
        fixed for the whole run, since agents do not yet move.
    estimator:
        The estimator instance that holds this agent's local estimate and
        local uncertainty, and that is updated from observations and, once
        peer fusion is implemented, from peer estimates.
    available:
        Whether the agent is currently contributing to sensing,
        communication and estimation. An unavailable agent represents a
        failed or temporarily disconnected agent.
    """

    def __init__(
        self,
        agent_id: str,
        position: State2D,
        estimator: "Estimator",
        available: bool = True,
    ) -> None:
        if not agent_id:
            raise ValueError("agent_id must be a non-empty string")
        self.agent_id = agent_id
        self.position = position
        self._estimator = estimator
        self.available = available

    @property
    def estimate(self):
        """This agent's current local state estimate."""
        return self._estimator.estimate()

    @property
    def covariance(self):
        """This agent's current local estimate covariance."""
        return self._estimator.covariance()

    def predict(self, dt: float) -> None:
        """Advance this agent's estimator through the process model."""
        self._estimator.predict(dt)

    def receive_observation(self, observation: "Observation") -> None:
        """Update this agent's local estimate from a direct measurement."""
        if observation.agent_id != self.agent_id:
            raise ValueError(
                "an agent may only receive an observation addressed to itself, "
                f"got observation for {observation.agent_id!r} at agent {self.agent_id!r}"
            )
        self._estimator.update(observation)

    def receive_peer_estimate(self, sender_id: str, mean, covariance) -> None:
        """Incorporate an estimate received from another agent through the
        communication layer. Never called directly by another Agent object;
        always routed through simulation.communication.channel.Channel.
        """
        self._estimator.incorporate_peer_estimate(sender_id, mean, covariance)
