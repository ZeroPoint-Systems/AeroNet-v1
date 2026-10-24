from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class ExperimentConfig:
    seed: int = 20261024
    agents: int = 6
    steps: int = 300
    dt: float = 1.0
    process_noise: float = 0.04
    measurement_noise: float = 0.30
    packet_loss: float = 0.10
    delay_probability: float = 0.10
    max_delay: int = 3
    disconnect_probability: float = 0.02
    disconnect_min_steps: int = 3
    disconnect_max_steps: int = 10
    communication_budget_per_agent: int = 60
    warning_threshold: float = 1.25
    reactive_threshold: float = 1.25
    prediction_horizon: int = 5
    network_radius: float = 1.1
    degradation_threshold: float = 1.0
    degradation_horizon: int = 5

    def validate(self):
        if self.agents < 2:
            raise ValueError("agents must be >= 2")
        if self.steps < 20:
            raise ValueError("steps must be >= 20")
        if self.dt <= 0:
            raise ValueError("dt must be > 0")
        if self.process_noise < 0 or self.measurement_noise <= 0:
            raise ValueError("process_noise must be >= 0 and measurement_noise must be > 0")
        for name in ("packet_loss", "delay_probability", "disconnect_probability"):
            value = getattr(self, name)
            if not 0 <= value < 1:
                raise ValueError(f"{name} must be in [0, 1)")
        if self.max_delay < 0:
            raise ValueError("max_delay must be >= 0")
        if self.disconnect_min_steps < 1 or self.disconnect_max_steps < self.disconnect_min_steps:
            raise ValueError("invalid disconnection duration range")
        if self.communication_budget_per_agent < 0:
            raise ValueError("communication budget must be >= 0")
        if self.prediction_horizon < 1 or self.degradation_horizon < 1:
            raise ValueError("prediction and degradation horizons must be >= 1")
        if self.network_radius <= 0:
            raise ValueError("network_radius must be > 0")
        if self.warning_threshold < 0 or self.reactive_threshold < 0 or self.degradation_threshold <= 0:
            raise ValueError("thresholds must be non-negative and degradation_threshold must be > 0")

    def save(self, path):
        Path(path).write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path):
        config = cls(**json.loads(Path(path).read_text(encoding="utf-8-sig")))
        config.validate()
        return config
