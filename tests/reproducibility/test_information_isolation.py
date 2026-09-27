"""Protects against the simulator accidentally giving an agent access to
ground truth. This sounds trivial. It is not: it is exactly the kind of
bug that would silently invalidate every experiment run against this
codebase, without producing any error or warning.
"""

from pathlib import Path

import numpy as np

from experiments.runners.config import load_config
from experiments.runners.run_experiment import build_world_and_agents
from simulation.core.state import State2D

REPO_ROOT = Path(__file__).resolve().parents[2]
PILOT_CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "pilot_001.yaml"


def test_agent_objects_hold_no_reference_to_world_or_truth():
    config = load_config(str(PILOT_CONFIG_PATH))
    rng = np.random.default_rng(0)
    world = build_world_and_agents(config, rng)

    forbidden_names = {"world", "true_state", "true_target_state", "ground_truth", "target"}
    for agent in world.swarm:
        assert forbidden_names.isdisjoint(vars(agent).keys())


def test_changing_ground_truth_does_not_change_an_existing_estimate():
    config = load_config(str(PILOT_CONFIG_PATH))
    rng = np.random.default_rng(0)
    world = build_world_and_agents(config, rng)

    agent = next(iter(world.swarm))
    estimate_before = agent.estimate.copy()

    # Directly and drastically change the ground truth, bypassing any
    # observation or communication event.
    world.true_target_state = State2D(x=-9999.0, y=9999.0)

    assert np.array_equal(agent.estimate, estimate_before)


def test_estimate_only_changes_through_an_explicit_observation():
    from simulation.sensing.observation import Observation

    config = load_config(str(PILOT_CONFIG_PATH))
    rng = np.random.default_rng(0)
    world = build_world_and_agents(config, rng)

    agent = next(iter(world.swarm))
    estimate_before = agent.estimate.copy()

    world.true_target_state = State2D(x=500.0, y=500.0)
    # still unchanged, no observation has occurred yet
    assert np.array_equal(agent.estimate, estimate_before)

    observation = Observation(
        agent_id=agent.agent_id,
        timestamp=0.0,
        value=world.true_target_state.as_array(),
        covariance=np.eye(2),
    )
    agent.receive_observation(observation)

    # only now, through the explicit observation channel, does the estimate move
    assert not np.array_equal(agent.estimate, estimate_before)
