"""The communication packet.

Agents never call one another directly. Every piece of information that
crosses from one agent to another passes through a Packet, so that
bandwidth, latency and packet loss can be modelled honestly, and so that a
communication cost can eventually be computed from something concrete
rather than assumed.
"""

from __future__ import annotations

import math
import pickle
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Packet:
    """A single message travelling from one agent to another.

    timestamp_delivered is None until the channel has decided, based on its
    latency and packet loss models, when or whether the packet arrives.
    """

    sender_id: str
    receiver_id: str
    timestamp_created: float
    payload: Any
    size_bytes: int = field(init=False)
    timestamp_delivered: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.sender_id or not self.receiver_id:
            raise ValueError("sender_id and receiver_id must be non-empty strings")
        if self.sender_id == self.receiver_id:
            raise ValueError("a packet cannot be addressed from an agent to itself")
        if not math.isfinite(self.timestamp_created):
            raise ValueError(f"timestamp_created must be finite, got {self.timestamp_created!r}")
        self.size_bytes = len(pickle.dumps(self.payload))

    def mark_delivered(self, timestamp: float) -> None:
        if self.timestamp_delivered is not None:
            raise ValueError(f"packet from {self.sender_id!r} to {self.receiver_id!r} already delivered")
        if timestamp < self.timestamp_created:
            raise ValueError(
                "a packet cannot be delivered before it was created: "
                f"created at {self.timestamp_created}, delivery requested at {timestamp}"
            )
        self.timestamp_delivered = timestamp
