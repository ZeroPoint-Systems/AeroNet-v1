import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "experiments" / "master_key" / "lab_v4" / "aeronet_lab_v4.py"
)
SPEC = importlib.util.spec_from_file_location("aeronet_lab_v4", SCRIPT)
LAB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAB)


def test_world_is_deterministic_for_a_seed():
    a = LAB.make_world(20261020)
    b = LAB.make_world(20261020)
    for left, right in zip(a, b):
        np.testing.assert_array_equal(left, right)


def test_sensor_model_has_heterogeneous_noise_and_missing_observations():
    assert len(set(LAB.SENSOR_SCALES.tolist())) == LAB.AGENTS
    assert len(set(LAB.OBSERVATION_PROBABILITIES.tolist())) == LAB.AGENTS

    _, observations, _, _ = LAB.make_world(20261020)
    missing = np.isnan(observations[:, :, 0]).sum(axis=0)
    assert np.all(missing > 0)
    assert np.all(missing < LAB.STEPS)


def test_communication_changes_some_estimates():
    result = LAB.run_trial(20261020, "periodic")
    assert result["attempted_broadcasts"] > 0
    assert result["delivered_links"] > 0
    assert result["state_changing_fusions"] > 0
    assert result["mean_fusion_state_delta"] > 0.0


def test_no_communication_sends_no_messages():
    result = LAB.run_trial(20261020, "none")
    assert result["attempted_broadcasts"] == 0
    assert result["delivered_links"] == 0
    assert result["state_changing_fusions"] == 0


def test_communicating_policies_have_matched_broadcast_budget():
    results = [
        LAB.run_trial(20261020, policy)
        for policy in ("periodic", "reactive", "predictive")
    ]
    budgets = [r["attempted_broadcasts"] for r in results]
    assert budgets == [budgets[0]] * len(budgets)
    assert budgets[0] > 0


def test_invalid_policy_is_rejected():
    try:
        LAB.run_trial(20261020, "invented")
    except ValueError:
        return
    raise AssertionError("Unknown policies must raise ValueError")
