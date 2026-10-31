# Cycle 3 report: mean-field sensing/communication mix planner

Branch `cdia-cycle1`. Frozen protocol: `docs/CYCLE3_PROTOCOL.md` (v1 frozen at 872212d, v2 addendum at 10aa4ca).
**Outcome: the planner reliably beats no communication, innovation-triggered communication and one-step CDIA, but it does not beat the best simple fixed schedule, and two of four frozen claims were falsified on held-out data. No novelty is established.**

## 1. Problem and decision
Cycle 2 showed that the split of a unit budget between fine-mode sensing and communication mattered far more than timing, and that one-step CDIA never found the sensing action. Cycle 3 therefore tests whether the best split can be **predicted from common-knowledge models**, per agent, instead of tuned. Test conditions: unequal sensing and communication cost, complementary (strongly anisotropic) sensors, loss, outages, topologies, agent counts.

## 2. Algorithm (`src/aeronet2/plan/meanfield.py`)
Each agent's budget B is split into a share m_i for transmissions and the rest for fine sensing (`SplitPeriodic` schedules). The planner scores a candidate set of shares by a **mean-field covariance recursion**: expected information per step replaces realised information, the Kalman information recursion gives P_j(t), and the objective is the mean over agents and steady-state steps of c' P_j(t) c, where c is the decision axis. Search: the 9 uniform shares (grid of eighths), then two coordinate-descent sweeps over per-agent shares. Complexity per candidate: O(N T) 4x4 operations; measured 1 to 2 s per plan in Python (about 105 candidate evaluations), computed once per scenario and shared by all agents. Online cost is nil; the schedule is periodic. Version 2 limits the fraction of messages that carry a fine measurement to `min(r_s/r_c, r_s * max_age)`, because a fine measurement can only be shared while younger than `window - 1 - delay_max` steps and only once.

**Mathematical result (proved, tested numerically).** For any distribution of delivered information increments, the expected variance of c.x_t under exact fusion is at least the variance computed from the expected increments (convexity of J -> e'J^-1 e, Jensen). The prediction is therefore optimistic, and the gap grows with delivery randomness. This is a short consequence of convexity and is unlikely to be new. A Monte Carlo test is in `tests/test_cdia.py`.

## 3. Evidence
Raw trial records: `results/cdia/raw_cycle3_validation.jsonl` (seeds 4000-4029, 8 configurations, 3,600 trials), `raw_cycle3_heldout.jsonl` (seeds 3000-3019, 6 configurations, 2,040 trials). Summaries: `summary_cycle3_*.json`. Primary outcome: decision-axis RMSE; matched unit budgets; paired intervals; Holm correction.

### Validation, planner v1 (frozen before the run)
| Claim | Result |
|---|---|
| C1 regret <= 5% in at least 6 of 8 | **Falsified.** Regret 8.0%, 12.0%, 10.4% in V5, V6, V7. |
| C2 beats 50/50 where predicted suboptimal (V2 to V5) | **Falsified in V4, V5.** V2, V3: communication-only chosen, 14% and 12% better than 50/50, not significant after Holm (p = 0.066, 0.10). |
| C5 beats communication-only | **Falsified.** Not better in 6 of 8; 10% worse in V7. |
| Beats none, innovation, one-step CDIA | Holds in all 8 for `none` and `innov_comm` (Holm p <= 0.04), and for `cdia` in 5 of 8 after correction. |
Cause found: the model credited every message with a fine measurement (see section 2).

### Held-out, planner v2 (changed after validation, checked only on development seeds 5000-5019, frozen at 10aa4ca)
| Config | Chosen share | Best grid share | Regret | Axis RMSE v2 / 50-50 / comm-only / none | v2 minus 50/50, minus comm-only (relative) |
|---|---|---|---|---|---|
| H1 8 agents | 1.0 | 1.0 | 0.0% | 0.749 / 0.906 / 0.749 / 1.103 | -17.3%, 0.0% |
| H2 complete | 0.5 | 0.875 | 8.1% | 0.589 / 0.589 / 0.564 / 1.099 | 0.0%, +4.4% |
| H3 line | 1.0 | 1.0 | 0.0% | 0.657 / 0.790 / 0.657 / 1.099 | -16.9%, 0.0% |
| H4 outage and loss 0.6 | 0.5 | 1.0 | 11.6% | 0.891 / 0.891 / 0.798 / 1.099 | 0.0%, **+11.6% [+1, +23]** |
| H5 sensor spread | 1.0 | 1.0 | 0.0% | 0.745 / 0.855 / 0.745 / 0.956 | -12.9%, 0.0% |
| H6 moving target | 0.375 | 0.875 | 3.9% | 1.107 / 1.121 / 1.100 / 1.371 | -1.3%, +0.7% |

| Claim | Result |
|---|---|
| A1 regret <= 5% in at least 5 of 6 | **Falsified.** Within 5% in 4 of 6; 8.1% (H2) and 11.6% (H4). |
| A2 not worse than 50/50 or communication-only | **Falsified.** In H4 it is 11.6% worse than communication-only (interval excludes 0; Holm p = 0.50). |
| A3 better than none, innovation, one-step CDIA | Point estimates favour the planner in all 18 contrasts (improvements 11 to 46%). Significant after Holm in 6/6 vs none, 4/6 vs innovation, 5/6 vs CDIA. |
| A4 per-agent shares equal uniform | Holds, but trivially: every plan was uniform. No heterogeneity benefit was found in any configuration, so the "information asymmetry" mechanism was not demonstrated. |
Planner v1 on the same held-out data (a comparison, not a claim) had regret up to 41% (H2), which shows the v2 fix mattered. Rank correlation of v2 predictions with simulation was 0.87 to 0.98 in H1, H3, H5 and 0.25 to 0.35 in H2, H4, H6.

## 4. What this establishes
- **Empirical, scoped:** in this simulated exact-fusion setting, combining fine sensing with communication under one budget beats innovation-triggered communication and one-step CDIA by 11 to 46% (held-out) in decision-axis RMSE, and the simple fixed rules (50/50, communication only) already capture most of that. The best fixed rule depends on cost and loss: communication only when sensing is costly and weak, an interior split otherwise.
- **Planner:** it selects the right rule in 4 of 6 held-out conditions (those with a sensing-heavy cost structure and a simple topology), and fails in complete topology and with outages plus heavy loss, where the mean-field model is misspecified (not yet diagnosed). It adds no demonstrated value over choosing between the two simple fixed rules.
- **Not established:** a benefit from per-agent allocation, any bound on decision loss, or any advantage over the best fixed schedule.

## 5. Literature comparison and novelty
Read in full: Baumann and Schön (arXiv:2304.00559): runtime choice between periodic and event-based scheduling with worst-case bounds, centralised. Trimpe (arXiv:1511.05223): event-based distributed estimation versus periodic. Bian, Chen and Li (arXiv:2309.08070): optimal threshold policy, single sensor. Calvo-Fullana and How (arXiv:2211.11038): mission-aware value of information censoring. None allocates a budget between sensing and communication, but the underlying tools are classical and **I have not read the primary sources**: offline sensor scheduling for linear-Gaussian estimation (Meier, Peschon and Dressler, 1967), convex sensor selection (Joshi and Boyd, 2009) and c-optimal design. Covariance-recursion scheduling for a directional objective is very likely covered by that work. **Novelty status: none established; treat the contribution as an engineering evaluation until those sources are read.**

## 6. Limitations
Single decision axis, linear-Gaussian target, one fine-mode factor per run, known models, identical sensing modes. Validation and held-out seeds are each used once. Planner v2 was changed after the validation result. Decision error is too noisy to support claims (reported only). No hardware evidence, no GPU work (not justified: planning takes seconds).

## 7. Reproduction
```
cd aeronet2 && export PYTHONPATH=src
python3 -m pytest tests -q                         # 65 passed, 1 skipped
python3 experiments/run_cycle3.py analyse validation
python3 experiments/run_cycle3.py analyse heldout  # both regenerate the summaries from the raw files
# re-simulation (refuses to overwrite): move raw_cycle3_*.jsonl aside, then
python3 experiments/run_cycle3.py run validation   # about 5 minutes on 2 cores
```
Environment used: Python 3.13, numpy 2.5.3, scipy 1.18.1, g++ 13 (the C++ kernel is optional).

## 8. Next strongest direction
Diagnose the mean-field error in complete topology and with outages (receiver dilution and availability), then test whether a **closed-loop** planner (re-planning from the agents' gossiped covariances and observed losses) removes the 8 to 12% regret. That is the one place where the data show an unresolved, falsifiable gap. Read the sensor-scheduling primary sources first, because they decide whether any of this is new.
