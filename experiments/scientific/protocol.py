from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import product
from typing import Any
import hashlib
import json


@dataclass(frozen=True)
class Condition:
    measurement_noise: float
    communication_range: float
    packet_loss_probability: float
    latency: float
    number_of_agents: int = 4

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def condition_id(self) -> str:
        payload = json.dumps(self.as_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Replicate:
    condition: Condition
    seed: int
    replicate: int
    baseline: str

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["condition"] = self.condition.as_dict()
        result["condition"]["condition_id"] = self.condition.condition_id()
        return result

    def experiment_id(self) -> str:
        return (
            f"{self.baseline}_"
            f"{self.condition.condition_id()}_"
            f"r{self.replicate:04d}_"
            f"s{self.seed}"
        )


def derive_seed(
    base_seed: int,
    condition_id: str,
    replicate: int,
    baseline: str,
) -> int:
    payload = f"{base_seed}|{condition_id}|{replicate}|{baseline}".encode()
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") % (2**32 - 1)


def build_protocol(
    measurement_noise: list[float],
    communication_range: list[float],
    packet_loss_probability: list[float],
    latency: list[float],
    number_of_agents: list[int],
    replicates: int,
    base_seed: int,
    baselines: list[str],
) -> list[Replicate]:
    conditions = [
        Condition(
            measurement_noise=noise,
            communication_range=radius,
            packet_loss_probability=loss,
            latency=delay,
            number_of_agents=agents,
        )
        for noise, radius, loss, delay, agents in product(
            measurement_noise,
            communication_range,
            packet_loss_probability,
            latency,
            number_of_agents,
        )
    ]

    experiments: list[Replicate] = []

    for condition in conditions:
        condition_id = condition.condition_id()

        for baseline in baselines:
            for replicate in range(replicates):
                seed = derive_seed(
                    base_seed,
                    condition_id,
                    replicate,
                    baseline,
                )

                experiments.append(
                    Replicate(
                        condition=condition,
                        seed=seed,
                        replicate=replicate,
                        baseline=baseline,
                    )
                )

    return experiments
