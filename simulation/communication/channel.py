"""The communication channel.

The channel is the single place where a message travelling between two
agents is subject to the communication graph, packet loss, and latency.
Agents and the experiment runner never bypass it. See simulation/README.md
for why this separation matters: it is what allows communication
conditions to be varied experimentally without touching agent code.
"""

from __future__ import annotations

from typing import Any, List

from simulation.communication.graph import CommunicationGraph
from simulation.communication.latency import FixedLatencyModel
from simulation.communication.packet import Packet
from simulation.communication.packet_loss import PacketLossModel


class Channel:
    """Applies connectivity, packet loss and latency to every message sent
    between agents, and holds packets until their scheduled delivery time.
    """

    def __init__(
        self,
        packet_loss_model: PacketLossModel,
        latency_model: FixedLatencyModel,
    ) -> None:
        self._packet_loss_model = packet_loss_model
        self._latency_model = latency_model
        self._pending: List[Packet] = []
        self._lost: List[Packet] = []

    def send(
        self,
        sender_id: str,
        receiver_id: str,
        payload: Any,
        created_time: float,
        graph: CommunicationGraph,
    ) -> None:
        """Attempt to send a message. Silently has no effect if the sender
        and receiver are not connected in the current graph; connectivity is
        a precondition for attempting to send, not itself a form of loss.
        """
        if not graph.has_edge(sender_id, receiver_id):
            return

        packet = Packet(
            sender_id=sender_id,
            receiver_id=receiver_id,
            timestamp_created=created_time,
            payload=payload,
        )

        if self._packet_loss_model.is_lost():
            self._lost.append(packet)
            return

        delivery_time = self._latency_model.delivery_time(created_time)
        packet.mark_delivered(delivery_time)
        self._pending.append(packet)

    def collect_deliverable(self, current_time: float) -> List[Packet]:
        """Return every packet whose scheduled delivery time has arrived,
        and remove them from the pending queue. A packet is never returned
        before its scheduled delivery time.
        """
        ready = [p for p in self._pending if p.timestamp_delivered <= current_time]
        self._pending = [p for p in self._pending if p.timestamp_delivered > current_time]
        return ready

    def lost_packets(self) -> List[Packet]:
        return list(self._lost)

    def pending_count(self) -> int:
        return len(self._pending)
