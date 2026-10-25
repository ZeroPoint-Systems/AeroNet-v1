import numpy as np
import pytest

from aeronet2.fusion import InfoFilter, predict_cov, sym
from aeronet2.model import (Scenario, prior, process_cov, sensor_R, simulate_measurements,
                            simulate_truth, transition)
from aeronet2.network import Network
from aeronet2.policies import ALL_POLICIES, Pacer
from aeronet2.rng import rng_for
from aeronet2.sim import centralised_rmse, run_trial, steady_state_pos_rmse
from aeronet2.stats import holm, paired_summary

FAST = Scenario(steps=160, burn_in=40)


# ---------------------------------------------------------------- randomness (v1 bug: seed overlap)
def test_streams_are_independent_across_seeds_and_agents():
    seen = set()
    for seed in range(30):
        for i in range(6):
            seen.add(tuple(rng_for(seed, "sensor", i).random(3)))
    assert len(seen) == 180  # v1 produced only 35 distinct noise streams for the same grid


def test_network_identical_across_calls_and_policies():
    n1, n2 = Network(FAST, 5), Network(FAST, 5)
    assert np.array_equal(n1._u, n2._u) and np.array_equal(n1.active, n2.active)


# ---------------------------------------------------------------- estimator correctness
def test_infofilter_equals_batch_solution_with_delay_and_reordering():
    sc = FAST.replace(delay_max=3)
    truth = simulate_truth(sc, 0)
    Z = simulate_measurements(sc, truth, 0)
    F, Q = transition(sc), process_cov(sc)
    Rinv = [np.linalg.inv(R) for R in sensor_R(sc)]
    f = InfoFilter(sc, 0)
    known, rng = {}, np.random.default_rng(0)
    inbox = {}
    T = 50
    for t in range(T):
        f.observe(t, Z[t, 0]); known[(0, t)] = Z[t, 0]
        for o in range(1, 6):
            if rng.random() < 0.7:
                inbox.setdefault(t + int(rng.integers(1, 4)), []).append((o, t))
        for (o, s) in inbox.pop(t, []):
            assert f.receive(o, s, Z[s, o], t)
            known[(o, s)] = Z[s, o]
    m, P = prior(sc)
    for k in range(T):
        if k:
            m, P = F @ m, predict_cov(P, F, Q)
        Y, y = np.zeros((4, 4)), np.zeros(4)
        for (o, s), z in known.items():
            if s == k:
                Y[:2, :2] += Rinv[o]; y[:2] += Rinv[o] @ z
        Pi = np.linalg.inv(P); P = sym(np.linalg.inv(Pi + Y)); m = P @ (Pi @ m + y)
    x, Pf = f.estimate()
    assert np.allclose(x, m, atol=1e-9) and np.allclose(Pf, P, atol=1e-9)


def test_duplicate_measurement_is_not_double_counted():
    f = InfoFilter(FAST, 0)
    z = np.array([0.3, -0.2])
    f.observe(0, z); f.observe(1, z)
    assert f.receive(1, 0, z, 1) is True
    before = f.estimate()[1].copy()
    assert f.receive(1, 0, z, 1) is False
    assert np.allclose(f.estimate()[1], before) and f.duplicates == 1


def test_stale_beyond_window_rejected_not_silently_used():
    f = InfoFilter(FAST, 0)
    for t in range(40):
        f.observe(t, np.zeros(2))
    assert f.receive(1, 5, np.zeros(2), 39) is False and f.too_old == 1


# ---------------------------------------------------------------- simulator vs analytic theory
def test_centralised_filter_matches_riccati_theory():
    sc = Scenario(steps=400, burn_in=60)
    emp = np.mean([centralised_rmse(sc, s) for s in range(12)])
    assert emp == pytest.approx(steady_state_pos_rmse(sc, list(range(6))), rel=0.07)


def test_local_filter_matches_riccati_and_is_consistent():
    sc = Scenario(steps=400, burn_in=60)
    rs = [run_trial(sc, "none", s) for s in range(10)]
    theory = np.mean([steady_state_pos_rmse(sc, [i]) for i in range(6)])
    assert np.mean([r.rmse_ss for r in rs]) == pytest.approx(theory, rel=0.07)
    assert 3.4 < np.mean([r.nees_ss for r in rs]) < 4.6      # 4-dof NEES for a consistent filter


# ---------------------------------------------------------------- accounting and budgets
@pytest.mark.parametrize("policy", ALL_POLICIES)
def test_accounting_and_budget(policy):
    sc = FAST.replace(outage_rate=0.03, loss=0.2, link_loss_spread=0.5, budget=15)
    r = run_trial(sc, policy, 3)
    a = r.accounting
    assert a["sent"] == a["delivered"] + a["lost_channel"] + a["lost_outage"] + a["lost_horizon"]
    if policy not in ("broadcast",):
        assert r.sent_per_agent <= sc.budget + 1e-9
    assert r.too_old == 0 and np.isfinite(r.rmse_ss)


def test_outages_actually_block_delivery():
    sc = FAST.replace(outage_rate=0.15, outage_min=5, outage_max=8)
    r = run_trial(sc, "broadcast", 1)
    assert r.accounting["lost_outage"] > 0


# ---------------------------------------------------------------- policy mechanics
def test_pacer_hits_target_rate_whatever_the_score_scale():
    rng = np.random.default_rng(0)
    for scale in (1e-3, 1.0, 1e3):
        p = Pacer(0.1)
        fires = [p.fire(scale * rng.exponential()) for _ in range(4000)]
        assert np.mean(fires[500:]) == pytest.approx(0.1, abs=0.03)


def test_reactive_score_is_noise_in_a_calibrated_filter():
    """v1 finding: innovation exceeds its 'event' threshold at the chi rate, i.e. it carries no information."""
    sc = Scenario(steps=300, burn_in=40)
    f = InfoFilter(sc, 0)
    truth = simulate_truth(sc, 2); Z = simulate_measurements(sc, truth, 2)
    frac = []
    for t in range(sc.steps):
        f.observe(t, Z[t, 0]); frac.append(f.last_innovation >= 1.25)
    assert np.mean(frac[40:]) == pytest.approx(np.exp(-1.25**2 / 2), abs=0.08)


# ---------------------------------------------------------------- statistics
def test_stats_refuse_nan_and_holm_is_monotone():
    with pytest.raises(ValueError):
        paired_summary([1.0, float("nan")], [1.0, 2.0])
    adj = holm({"a": 0.01, "b": 0.02, "c": 0.5})
    assert adj["a"] <= adj["b"] <= adj["c"] and adj["a"] == pytest.approx(0.03)


def test_paired_summary_detects_a_real_difference_and_equivalence():
    rng = np.random.default_rng(1)
    base = 1 + 0.05 * rng.standard_normal(40)
    s = paired_summary(base - 0.05, base, margin=0.1)
    assert s["ci_hi"] < 0 and s["p_signflip"] < 0.01
    s2 = paired_summary(base + 1e-4 * rng.standard_normal(40), base, margin=0.01)
    assert s2["equivalent_within_margin"]
