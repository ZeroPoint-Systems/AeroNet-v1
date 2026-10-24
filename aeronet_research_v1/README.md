# AeroNet Research Baseline

A reproducible simulation for comparing decentralised estimation and communication policies under a shared-state tracking model.

## Research question

Can a local innovation-trend heuristic reduce estimation error or improve early warning of subsequent estimator degradation under a fixed per-agent communication-event budget, compared with no communication, periodic communication and a reactive innovation policy?

This is a research baseline, not a claim of novelty or superiority.

## Setup and run (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m aeronet.experiment --config configs/default.json --seeds 30 --output results
```

## Methods

- Constant-velocity state `[x, y, vx, vy]` with a bounded deterministic manoeuvre and process noise.
- Independent local Kalman filters using noisy position-only observations.
- Bounded peer-state correction without treating peer estimates as independent measurements.
- Seeded exogenous packet loss, delays and temporary node disconnections.
- Four policies: no communication, periodic, reactive and predictive.
- Per-trial results, summary statistics and paired bootstrap confidence intervals against the no-communication baseline.

## Metrics and limitations

Position RMSE is pooled over agents and timesteps. Warning metrics compare predictive-policy warnings against a fixed, preconfigured future position-error threshold. They measure the warning heuristic, not an established physical failure mode. The same numeric threshold is not necessarily calibrated across every system or scenario.

The exogenous loss and delay schedules are seeded, but connectivity depends on estimated agent positions, which can differ between policies. Therefore, the experiment is not a perfect common-random-number comparison of all network events. The report's paired confidence intervals describe matched seeds, not identical realised trajectories or independent physical replications.

The per-agent budget limits communication events initiated by each agent. Each event attempts a transmission to every other agent, and the reported message count counts each recipient attempt, including attempts dropped due to link state or packet loss. The budget is therefore not a byte budget and must not be described as one.

Before claiming superiority, test multiple independently specified network regimes, freeze thresholds on development seeds, evaluate on held-out seeds, include appropriate published baselines, and investigate sensitivity to model assumptions. Confidence intervals do not establish novelty or causal validity.

This is not flight-control software and must not be deployed to real aircraft.

## Outputs

- `results/trials.json`: detailed trial results.
- `results/trials.csv`: compact trial-level metrics.
- `results/summary.json`: configuration, policy summaries and paired bootstrap intervals.

## Research integrity

Passing tests establishes only the tested software properties. It does not demonstrate scientific novelty, practical applicability, or superiority over prior work.
