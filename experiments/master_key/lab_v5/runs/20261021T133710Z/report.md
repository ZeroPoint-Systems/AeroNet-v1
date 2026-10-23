# AeroNet Lab v5 exploratory benchmark

Synthetic simulation only. Results are not physical validation or proof of novelty.

## Policy results

| Policy | Mean RMSE | RMSE SD | Mean broadcasts | Mean delivered links |
|---|---:|---:|---:|---:|
| none | 1.942986 | 0.093533 | 0.0 | 0.0 |
| periodic | 1.584406 | 0.047489 | 360.0 | 1615.8 |
| reactive | 1.737877 | 0.039965 | 248.4 | 1109.8 |
| predictive | 1.772605 | 0.049464 | 230.6 | 1031.3 |

## Paired adaptive-versus-periodic RMSE

- **reactive_minus_periodic:** mean difference +0.153471; 95% paired bootstrap interval [+0.134950, +0.171184]; lower RMSE in 0/20 seeds; mean broadcast change -31.0%.
- **predictive_minus_periodic:** mean difference +0.188200; 95% paired bootstrap interval [+0.167097, +0.210262]; lower RMSE in 0/20 seeds; mean broadcast change -35.9%.

## Interpretation limits

- These 20 seeds were used for exploration and are not a held-out evaluation.
- Thresholds were inherited from Lab v4 and were not optimised here.
- Lower communication may trade off against estimation accuracy.
- A positive or negative result does not by itself establish a novel scientific contribution.
