# CDIA, cycle 1 report

Branch `cdia-cycle1` (local, from `revamp` b3a6b3e). Status: **no demonstrated advantage; not novel on the evidence so far.**

## 1. What was built

| Part | File | Notes |
|---|---|---|
| Decision value | `src/aeronet2/cdia/decision.py` | Expected reduction in Bayes decision error from one measurement, for a receiver with covariance P. |
| Dual-mode filter | `src/aeronet2/cdia/filters.py` | Delay-tolerant exact fusion with a nominal and a fine sensing mode (origins N..2N-1). |
| Allocation policies | `src/aeronet2/cdia/policy.py` | `cdia`, `cdia_comm`, `trace_joint`, `trace_comm`, split-periodic, and labelled hindsight oracles. |
| Trial runner | `src/aeronet2/cdia/sim.py` | One action per agent per step; one shared budget in units (send = 1, fine sensing = `sense_cost`). |
| C++ kernel | `cpp/cdia_value.cpp` | Same fixed-grid rule as Python, C ABI, batch entry point. |
| Experiments | `experiments/run_cdia.py`, `experiments/diag_headroom.py` | Raw per-trial JSONL written once (`open(..., "x")`), separate analysis stage. |
| Tests | `tests/test_cdia.py` | 45 pass, 1 skipped (unbudgeted reference). |

Not built: the compute action, correlated sensor noise with its own filter, a published distributed-estimation baseline, CUDA.

## 2. Mathematical specification

Team decision: agent i acts on sign(c.x - tau). For a Gaussian belief N(tau + d, s2) of u = c.x the Bayes error is Phi(-|d| / s).
A position measurement with covariance R, received by an agent with covariance P, has posterior-mean step variance
v = c'P H'(H P H' + R)^-1 H P c and leaves variance s2 - v. The counterfactual value is

    V(d, s2, v) = Phi(-|d|/s) - E_xi Phi(-|d + sqrt(v) xi| / sqrt(s2 - v)),   xi ~ N(0, 1).

Decentralised approximation, assumptions stated:
1. The receiver's covariance is inferred by the sender (PeerModel, refreshed by gossiped covariances).
2. The sender's own mean stands in for the receiver's mean when forming d.
3. Information age: the measurement noise is inflated by the process noise accumulated over the expected delay
   (and over the age of a stored fine measurement).
4. Actions are scored by V / cost and paced by the AeroNet2 quantile pacer to the remaining budget.

Proved or tested properties (`tests/test_cdia.py`): 0 <= V <= current Bayes error; V = 0 without information and
far from the boundary; V matches a 600,000-sample Monte Carlo simulation of the Gaussian model within 4 standard
errors; a second identical measurement has lower value (redundancy through the updated covariance); the matrix form
reduces to the scalar form; the C++ kernel agrees with Python to 1e-12; the budget is never exceeded; communication
decisions do not change when only the evaluation ground truth changes. The quadrature is numerical, so these are tested
properties, not theorems. No bound on collective decision loss has been derived.

## 3. Experiment (empirical finding)

Scenario fixed from a pilot on development seeds 1000 to 1009 (6 agents, ring, `sigma` 2.5, sensor spread 0.7, `q` 1e-4, 200 steps).
Main run: 30 validation seeds (2000 to 2029), budgets 5, 10, 20 units, paired by seed. Primary outcome: team decision error rate.
Raw records: `results/cdia/raw_main.jsonl`; summary: `results/cdia/summary_main.json`.

Decision error (%), selected cells (full table in the summary file):

| Policy | B=10 error | B=10 units used | B=20 error | B=20 units used |
|---|---|---|---|---|
| none | 1.49 | 0 | 1.49 | 0 |
| periodic_comm | 1.33 | 10.0 | 1.51 | 20.0 |
| periodic_split | 1.42 | 9.5 | 1.30 | 19.5 |
| innov_comm | 1.53 | 9.6 | 1.84 | 19.4 |
| trace_joint | 1.37 | 6.6 | 1.30 | 14.5 |
| cdia | 1.71 | 2.9 | 1.39 | 4.1 |
| broadcast (reference) | 0.67 | 400 | 0.67 | 400 |

All 9 paired CDIA contrasts (against `trace_joint`, `periodic_split`, `innov_comm` at three budgets) are non-significant
after Holm correction (smallest adjusted p = 0.56). At budget 10 the point estimates favour the references.

Headroom diagnostic (`results/cdia/raw_headroom.jsonl`), same seeds: hindsight oracles that act only while the decision is
contested reach 1.2 to 1.4% against 1.5% for periodic and 1.49% for no communication; standard error per cell is about 0.6.

## 4. Interpretation

1. The 10-seed pilot suggested CDIA (1.8%) beat periodic (3.0%) at a fifth of the budget. That did not replicate on 30 seeds. It was noise.
2. The scenario has almost no headroom for a budgeted policy: the best conceivable allocation removes about 0.2 points, below what 30 seeds can resolve. No allocation method could be distinguished here, so this experiment neither supports nor refutes CDIA. It only shows CDIA is not better than simple alternatives where the question is testable at all.
3. Hypothesis (untested): the one-step decision value ignores persistence. With small process noise a shared measurement keeps improving later estimates, so most of the benefit of broadcast (0.67%) comes from continuous accumulation, not from information delivered at the moment of decision. If so, a myopic decision value is the wrong utility, and a horizon-aware value is the better formulation.
4. CDIA spends 2 to 4 units of a 5 to 20 budget. Because it scores zero far from the boundary and the pacer cannot track scores spanning many orders of magnitude, part of this is a pacing artefact. The oracle result suggests it is not the main cause.
5. Performance: Python decision value costs about 78 microseconds per evaluation (0.31 ms per agent decision including peer-model upkeep); the C++ kernel costs about 119 microseconds, so it is **slower** than the vectorised Python (no precomputed weights, 4001 `erfc` calls). It is kept for onboard portability, not speed. CUDA was not built: no GPU or `nvcc` in this environment, and each evaluation is far too small to benefit.

## 5. Prior work

- Calvo-Fullana and How, "Mission-Aware Value of Information Censoring for Distributed Filtering", arXiv:2211.11038 (full text read): mission-aware VoI for distributed filtering. KL-divergence test with a mission constraint through dual variables, single threshold, no budget, no delay or loss model, no sensing or computation actions, one simulated scenario, no theorems. CDIA differs in using Bayes decision error, inferred receiver covariance, delay-aware noise and a joint sensing and communication budget, but the central idea of mission-aware information value is not new.
- Baumann and Schön, arXiv:2304.00559, and Trimpe, arXiv:1511.05223 (both read earlier, see the audit report) cover event-based against periodic estimation.
- Decision-theoretic value of information and task-driven sensor management are older fields that I have not yet read. Novelty of any decision-error VoI utility should be treated as unlikely until that is done.

**Novelty status: none established.**

## 6. Process notes

- The main run was started before the tests were written. The tests then passed without code changes, so the results stand, but the order should be known.
- Seeds 3000 to 3019 (held-out plan in `run_cdia.py`) were deliberately not used, because running them on an algorithm with no headroom would spend the confirmation set for nothing.
- `results/cdia/` raw files must not be edited; the writer refuses to overwrite.

## 7. Next

See `CDIA_STATUS.md`. In order: find a scenario with real headroom (oracle-to-periodic gap above 20% relative), test the persistence hypothesis with a horizon-aware value, then add correlated noise, the compute action and a published baseline.
