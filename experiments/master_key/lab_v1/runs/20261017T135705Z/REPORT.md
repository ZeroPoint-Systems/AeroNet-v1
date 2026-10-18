# AeroNet exploratory tracking benchmark

This is an initial synthetic benchmark, not a novelty claim.

- Agents: 6
- Steps per trial: 300
- Paired seeds: 20

## Mean RMSE
- none: 0.234400 (SD 0.018687); mean messages 0.0
- periodic: 0.135823 (SD 0.009391); mean messages 300.0
- adaptive: 0.125077 (SD 0.008160); mean messages 300.0

## Adaptive minus periodic
- Mean paired difference: -0.010747
- Bootstrap interval: [-0.012738806720857771, -0.008631857382413495]

## Files
- trial_results.csv: per-seed results
- rmse_by_time.csv: time-series averages
- rmse_plot.svg: generated figure
- summary.json: configuration and summary statistics

## Limitations
- Synthetic constant-velocity target and simplified sensor model.
- Centralised policy selection is used for this exploratory comparison.
- The adaptive heuristic is not claimed as novel.
- No Gazebo, ROS 2 or physical flight validation is included.
- Further baselines, model checks, and independent validation are required.