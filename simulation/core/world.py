"""World: the container for simulation ground truth.

The World is the only object in the simulator permitted to hold the true
target state. It is read by the sensing layer, in order to generate
observations, and by the analysis layer, in order to score estimates
against ground truth. It must never be read by an Agent, by an Estimator,
or by anything inside simulation.communication.

In the sprint 1 configuration the target is static, so World does not yet
implement target dynamics. That is deliberate: introducing a moving target
before the estimation and communication machinery has been validated on a
static target would make it impossible to tell which change caused any
observed effect.
"""

from __future__ import annotations

from simulation.core.state import State2D
from simulation.core.swarm import Swarm
from simulation.core.time import SimulationClock


class World:
    """The simulation environment: ground truth, the swarm, and the clock."""

    def __init__(
        self,
        true_target_state: State2D,
        swarm: Swarm,
        clock: SimulationClock,
    ) -> None:
        self.true_target_state = true_target_state
        self.swarm = swarm
        self.clock = clock

    def step(self) -> float:
        """Advance the simulation clock by one step.

        Target dynamics, once introduced, will be advanced here as well.
        For now the target does not move, so this only advances the clock.
        """
        return self.clock.step()
