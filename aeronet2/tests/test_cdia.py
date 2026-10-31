import ctypes
import os
import subprocess

import numpy as np
import pytest

from aeronet2.cdia.decision import bayes_error, decision_value, info_variance, measurement_value
from aeronet2.cdia.filters import DualModeFilter
from aeronet2.cdia.sim import Decision, POLICIES, run_trial
from aeronet2.fusion import meas_update_cov
from aeronet2.model import Scenario, simulate_measurements, simulate_truth

SC = Scenario(q=1e-4, prior_vel_var=0.04, prior_pos_var=1.0, sigma=2.5, sensor_spread=0.7, anisotropy=4,
              steps=80, burn_in=20, budget=8)
DEC = Decision()


def test_value_is_bounded_by_current_error():
    rng = np.random.default_rng(1)
    for _ in range(300):
        s2 = rng.uniform(0.05, 4.0)
        v = rng.uniform(0.0, 0.95) * s2
        d = rng.normal(0, 2.0)
        val = decision_value(d, s2, v)
        assert -1e-4 <= val <= bayes_error(d, s2) + 1e-4


def test_value_vanishes_without_information_or_far_from_boundary():
    assert decision_value(0.3, 1.0, 0.0) == 0.0
    assert decision_value(12.0, 1.0, 0.5) < 1e-12


def test_value_matches_monte_carlo():
    rng = np.random.default_rng(2)
    n = 600_000
    for d, s2, r in [(0.0, 1.0, 1.0), (0.7, 0.8, 0.5), (1.5, 2.0, 3.0)]:
        u = rng.normal(d, np.sqrt(s2), n)
        y = u + rng.normal(0, np.sqrt(r), n)
        post_mean = d + s2 / (s2 + r) * (y - d)
        wrong_before = (d > 0) != (u > 0)
        wrong_after = (post_mean > 0) != (u > 0)
        diff = wrong_before.astype(float) - wrong_after.astype(float)
        se = diff.std() / np.sqrt(n)
        v = s2 * s2 / (s2 + r)
        assert abs(diff.mean() - decision_value(d, s2, v)) < 4 * se + 2e-4


def test_matrix_form_reduces_to_scalar_form():
    P = np.diag([1.5, 1.5, 0.3, 0.3])
    R = 0.5 * np.eye(2)
    c4 = np.array([1.0, 0.0, 0.0, 0.0])
    assert info_variance(P, R, c4) == pytest.approx(1.5**2 / (1.5 + 0.5))
    assert measurement_value(P, R, c4, 0.4) == pytest.approx(decision_value(0.4, 1.5, 1.5**2 / 2.0))


def test_second_identical_measurement_is_worth_less():
    P = np.diag([2.0, 2.0, 0.5, 0.5])
    R = 1.0 * np.eye(2)
    c4 = np.array([1.0, 0.0, 0.0, 0.0])
    first = measurement_value(P, R, c4, 0.3)
    second = measurement_value(meas_update_cov(P, R), R, c4, 0.3)
    assert second < first


def test_dual_mode_filter_uses_fine_measurement_once():
    f = DualModeFilter(SC, 0, kappa=4.0)
    f.observe(0, np.zeros(2))
    tr0 = np.trace(f.estimate()[1])
    f.add_fine(0, np.zeros(2))
    assert np.trace(f.estimate()[1]) < tr0
    assert f.receive(SC.n_agents, 0, np.zeros(2), 0) is False   # origin N + 0 at t=0 already seen
    assert f.duplicates == 1


@pytest.mark.parametrize("policy", POLICIES)
def test_budget_is_never_exceeded(policy):
    if policy == "broadcast":
        pytest.skip("reference policy without a budget")
    r = run_trial(SC, policy, 11, DEC)
    assert r.units_per_agent <= SC.budget + 1e-9


def test_trials_are_deterministic():
    a = run_trial(SC, "cdia", 5, DEC)
    b = run_trial(SC, "cdia", 5, DEC)
    assert (a.decision_error, a.rmse_ss, a.units_per_agent, a.bytes_sent) == (b.decision_error, b.rmse_ss, b.units_per_agent, b.bytes_sent)


@pytest.mark.parametrize("policy", ["cdia_comm", "trace_comm", "innov_comm", "periodic_comm"])
def test_communication_decisions_do_not_depend_on_ground_truth(policy):
    truth = simulate_truth(SC, 3)
    Z = simulate_measurements(SC, truth, 3)
    a = run_trial(SC, policy, 3, DEC, truth=truth, Z=Z)
    shifted = truth.copy()
    shifted[:, 0] += 5.0            # evaluation target moves, agents' data do not
    b = run_trial(SC, policy, 3, DEC, truth=shifted, Z=Z)
    assert (a.sent_per_agent, a.bytes_sent, a.rmse_ss == b.rmse_ss) == (b.sent_per_agent, b.bytes_sent, False)


def test_cpp_kernel_matches_python(tmp_path):
    src = os.path.join(os.path.dirname(__file__), "..", "cpp", "cdia_value.cpp")
    lib = tmp_path / "libcdia.so"
    try:
        subprocess.run(["g++", "-O2", "-shared", "-fPIC", "-std=c++17", src, "-o", str(lib)], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("no C++ compiler")
    f = ctypes.CDLL(str(lib)).cdia_decision_value
    f.restype = ctypes.c_double
    f.argtypes = [ctypes.c_double] * 3
    rng = np.random.default_rng(4)
    for _ in range(200):
        s2 = rng.uniform(0.05, 4.0)
        v = rng.uniform(0.0, 0.95) * s2
        d = rng.normal(0, 2.0)
        assert f(d, s2, v) == pytest.approx(decision_value(d, s2, v), abs=1e-12)
