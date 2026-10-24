from aeronet.config import ExperimentConfig
from aeronet.simulation import run_trial


def test_trial_reproducible():
    c = ExperimentConfig(agents=3, steps=30, communication_budget_per_agent=5)
    a = run_trial(c, 42, "predictive")
    b = run_trial(c, 42, "predictive")
    assert a["position_rmse"] == b["position_rmse"]
    assert a["messages_sent"] == b["messages_sent"]


def test_budget_and_delivery_accounting():
    c = ExperimentConfig(agents=3, steps=30, communication_budget_per_agent=4,
                         packet_loss=0, delay_probability=0, disconnect_probability=0,
                         network_radius=100)
    row = run_trial(c, 11, "periodic")
    assert max(row["per_agent_budget_used"]) <= 4
    assert row["messages_sent"] == row["messages_delivered"] + row["messages_dropped"]


def test_all_policies_run():
    c = ExperimentConfig(agents=3, steps=30, communication_budget_per_agent=3)
    for name in ("none", "periodic", "reactive", "predictive"):
        row = run_trial(c, 5, name)
        assert row["position_rmse"] >= 0
