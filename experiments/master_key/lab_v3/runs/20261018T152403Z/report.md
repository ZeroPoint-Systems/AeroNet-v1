# AeroNet Lab v3 validation benchmark

This is an exploratory synthetic simulation, not real-world validation.

- Paired seeds: 20
- Agents: 6
- Steps per trial: 300
- Packet loss probability per link: 10%
- Delay: 1-3 steps

## Results

| Policy | Mean RMSE | SD RMSE | Mean broadcasts | Mean delivered links | State-changing fusions |
|---|---:|---:|---:|---:|---:|
| none | 1.277729 | 0.024799 | 0.0 | 0.0 | 0.0 |
| periodic | 1.277729 | 0.024799 | 360.0 | 1615.8 | 0.0 |
| reactive | 1.277729 | 0.024799 | 360.0 | 1600.8 | 0.0 |
| predictive | 1.277729 | 0.024799 | 360.0 | 1601.3 | 0.0 |

## Paired RMSE differences against no communication

Negative differences favour the communication policy.

| Comparison | Mean difference | Approximate 95% interval | Seeds improved |
|---|---:|---:|---:|
| periodic_minus_none | -0.000000 | [-0.000000, -0.000000] | 60% |
| reactive_minus_none | 0.000000 | [-0.000000, 0.000000] | 40% |
| predictive_minus_none | 0.000000 | [-0.000000, 0.000000] | 35% |

## Limitations

- Synthetic constant-velocity model with stochastic acceleration.
- All agents observe the same target, with independent sensor noise.
- The predictive policy is a fixed heuristic, not a trained predictor.
- Pairwise covariance intersection is applied repeatedly; cross-correlation handling requires further study.
- The paired confidence intervals are approximate.
- This is not a real-drone or real-dataset validation.

## Interpretation

A non-zero fusion count shows that received messages changed an estimate or covariance. It does not by itself demonstrate improved accuracy. Compare RMSE, delivery rate and communication cost together.
