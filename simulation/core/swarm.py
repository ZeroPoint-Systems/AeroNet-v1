"""Swarm abstraction: a managed collection of agents.

The swarm does not implement any estimation or control logic. It only
manages membership, and reports the counts that later become experimental
variables, in particular the distinction between the total number of
agents and the number currently available.
"""

from __future__ import annotations

from typing import Dict, Iterator, List

from simulation.core.agent import Agent


class DuplicateAgentIDError(Exception):
    """Raised when an agent is added under an ID that is already in use."""


class UnknownAgentIDError(Exception):
    """Raised when an operation refers to an agent ID that is not present."""


class Swarm:
    """A collection of Agent objects, indexed by agent_id."""

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}

    def add_agent(self, agent: Agent) -> None:
        if agent.agent_id in self._agents:
            raise DuplicateAgentIDError(
                f"an agent with id {agent.agent_id!r} already exists in this swarm"
            )
        self._agents[agent.agent_id] = agent

    def remove_agent(self, agent_id: str) -> None:
        if agent_id not in self._agents:
            raise UnknownAgentIDError(f"no agent with id {agent_id!r} in this swarm")
        del self._agents[agent_id]

    def get_agent(self, agent_id: str) -> Agent:
        if agent_id not in self._agents:
            raise UnknownAgentIDError(f"no agent with id {agent_id!r} in this swarm")
        return self._agents[agent_id]

    def active_agents(self) -> List[Agent]:
        """All agents currently marked available."""
        return [a for a in self._agents.values() if a.available]

    def all_agents(self) -> List[Agent]:
        """Every agent in the swarm, available or not."""
        return list(self._agents.values())

    def agent_count(self) -> int:
        """N_total: the total number of agents in the swarm, available or not."""
        return len(self._agents)

    def available_agent_count(self) -> int:
        """N_available: the number of agents currently marked available."""
        return len(self.active_agents())

    def failed_agent_count(self) -> int:
        """N_failed: the number of agents currently marked unavailable."""
        return self.agent_count() - self.available_agent_count()

    def __iter__(self) -> Iterator[Agent]:
        return iter(self._agents.values())

    def __len__(self) -> int:
        return self.agent_count()
