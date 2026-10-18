# AeroNet Lab v2 exploratory results

This is a software benchmark, not a novelty claim.

- Paired seeds: 20
- Agents: 6
- Steps per trial: 300
- Packet loss per link: 10%
- Delay: 1-3 steps

## Mean position RMSE

| Policy | Mean RMSE | SD | Mean attempted broadcasts | Mean delivered links |
|---|---:|---:|---:|---:|
| none | 1.277729 | 0.024799 | 0.0 | 0.0 |
| periodic | 1.277729 | 0.024799 | 360.0 | 1619.2 |
| reactive | 1.277729 | 0.024799 | 360.0 | 1596.5 |
| predictive | 1.277729 | 0.024799 | 360.0 | 1598.2 |

## Paired comparisons

- **predictive_minus_reactive:** mean difference 0.000000; bootstrap interval [-2.55351295663786e-16, 9.992007221626409e-16]; fraction with first policy better 0.30
- **predictive_minus_periodic:** mean difference 0.000000; bootstrap interval [-2.7755575615628914e-16, 1.3433698597964394e-15]; fraction with first policy better 0.30
- **reactive_minus_periodic:** mean difference 0.000000; bootstrap interval [-7.327471962526033e-16, 9.992007221626409e-16]; fraction with first policy better 0.35

## Interpretation rules

- Lower RMSE is better.
- A negative paired difference favours the first named policy.
- A bootstrap interval is not proof of novelty or generalisation.
- The policies must be checked for implementation correctness before interpreting differences.
- The predictive heuristic is not a trained or calibrated forecasting model.

## Limitations

- Synthetic constant-velocity tracking with stochastic acceleration.
- Abstract agents, not physical drones.
- Covariance intersection is a simplified reference fusion method.
- Predictive score is a fixed heuristic and is not yet calibrated.
- Communication cost is measured as attempted broadcasts and delivered links.
- One transmission opportunity per agent per window matches counts, but does not establish optimal scheduling.
- No literature review or novelty claim is included.
- Held-out scenario families and formal hypothesis testing remain future work.