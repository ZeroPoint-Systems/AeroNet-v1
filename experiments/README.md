# experiments/

Actual experimental campaigns. Frozen protocols in, immutable raw data out.

- `protocols/`, frozen protocols. Do not casually edit these after results appear; version them.
- `configs/`, one config per experiment. A result should always be traceable to: configuration,
  code version, random seed, date, algorithm version, simulator version.
- `pilot/`, small experiments to detect bugs and check the protocol works. Pilot results do not
  become the main dataset unless explicitly justified.
- `main/`, the primary scientific dataset, used for the main claims.
- `ablations/`, remove one component at a time (adaptive sensing, adaptive communication,
  adaptive motion, geometry adaptation, failure handling, information metric) to determine what
  actually causes any improvement.
- `adversarial/`, deliberately hostile conditions (high packet loss, large latency, sensor bias,
  sensor dropout, agent failure, network fragmentation, poor geometry, rapid environmental
  change).
- `scaling/`, sweep swarm size `N` within justified computational/physical limits.
- `hardware_validation/`, experiments that compare simulation predictions with physical
  measurements. For each: record simulation prediction, hardware condition, measured result,
  difference, possible explanation.
- `raw/`, never modify once written; treat as immutable.
- `processed/`, derived data; every processed dataset must be traceable back to raw data.
- `manifests/`, one manifest per experiment.

## Manifest fields
```text
experiment_id
git_commit
configuration
seed
hardware_version
software_version
timestamp
dataset
status
```
