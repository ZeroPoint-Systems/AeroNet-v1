# AeroNet Lab v4 benchmark report

Run: `20261021T093229Z` UTC
Seeds: 20 paired seeds, 20261020 to 20261039
Agents: 6; steps per trial: 300

## Policy results

| Policy | Mean RMSE | SD RMSE | Mean broadcasts | Mean delivered links | Mean state-changing fusions |
|---|---:|---:|---:|---:|---:|
| none | 1.942986 | 0.093533 | 0.0 | 0.0 | 0.0 |
| periodic | 1.584406 | 0.047489 | 360.0 | 1615.8 | 210.2 |
| reactive | 1.586871 | 0.050388 | 360.0 | 1605.8 | 233.3 |
| predictive | 1.588139 | 0.052157 | 360.0 | 1604.2 | 227.0 |

## Paired RMSE comparisons

- **periodic_minus_none:** mean difference -0.358580, approximate 95% CI [-0.399442, -0.317718], n=20.
- **reactive_minus_none:** mean difference -0.356115, approximate 95% CI [-0.389755, -0.322474], n=20.
- **predictive_minus_none:** mean difference -0.354847, approximate 95% CI [-0.388273, -0.321420], n=20.

Negative policy-minus-none RMSE indicates lower error than no communication.

## Limitations

- Synthetic target dynamics and observation model.
- Sensor capabilities are deliberately heterogeneous.
- Covariance intersection is a conservative track-fusion baseline.
- The predictive policy is a hand-designed heuristic, not a trained model.
- Approximate confidence intervals are exploratory; no multiplicity correction is applied.
- No claim of novelty, real-world performance, or causal mechanism is established by this benchmark.
