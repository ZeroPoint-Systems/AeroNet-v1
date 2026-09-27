"""The communication graph.

G_t = (V, E_t): an edge exists between two agents if they are currently
able to communicate. Sprint 1 uses the simplest possible rule, a fixed
communication range, so that the graph is a straightforward function of
agent positions. Bandwidth, message size and more elaborate topology
rules are layered on top of this graph later, in channel.py, rather than
folded into the graph definition itself.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from simulation.core.agent import Agent


class CommunicationGraph:
    """An undirected graph over available agents, built from a range rule.

    ASSUMPTION: communication is symmetric, range based, and does not model
    obstructions or line of sight. This is a deliberately simple baseline.
    """

    def __init__(self, agents: List[Agent], communication_range: float) -> None:
        if communication_range < 0:
            raise ValueError(f"communication_range must not be negative, got {communication_range!r}")
        self._communication_range = communication_range
        self._edges: Set[Tuple[str, str]] = set()
        self._adjacency: Dict[str, Set[str]] = {a.agent_id: set() for a in agents}

        available = [a for a in agents if a.available]
        for i, agent_a in enumerate(available):
            for agent_b in available[i + 1 :]:
                distance = agent_a.position.distance_to(agent_b.position)
                if distance <= communication_range:
                    key = tuple(sorted((agent_a.agent_id, agent_b.agent_id)))
                    self._edges.add(key)
                    self._adjacency[agent_a.agent_id].add(agent_b.agent_id)
                    self._adjacency[agent_b.agent_id].add(agent_a.agent_id)

    @property
    def communication_range(self) -> float:
        return self._communication_range

    def has_edge(self, agent_id_a: str, agent_id_b: str) -> bool:
        return tuple(sorted((agent_id_a, agent_id_b))) in self._edges

    def neighbours(self, agent_id: str) -> Set[str]:
        return set(self._adjacency.get(agent_id, set()))

    def edges(self) -> Set[Tuple[str, str]]:
        return set(self._edges)

    def edge_count(self) -> int:
        return len(self._edges)
