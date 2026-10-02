from simulation.core.state import State2D
from simulation.core.swarm import Swarm
from simulation.core.time import SimulationClock
from simulation.core.world import World


def test_world_holds_target_swarm_and_clock():
    target = State2D(3.0, 4.0)
    swarm = Swarm()
    clock = SimulationClock(dt=0.5)

    world = World(true_target_state=target, swarm=swarm, clock=clock)

    assert world.true_target_state is target
    assert world.swarm is swarm
    assert world.clock is clock


def test_step_advances_clock_without_changing_static_target():
    target = State2D(3.0, 4.0)
    world = World(
        true_target_state=target,
        swarm=Swarm(),
        clock=SimulationClock(dt=0.5),
    )

    assert world.step() == 0.5
    assert world.clock.step_index == 1
    assert world.true_target_state is target
