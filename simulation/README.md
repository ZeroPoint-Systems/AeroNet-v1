# simulation/

The simulator is not a demonstration, it is the main **controlled experimental instrument** for
AeroNet. Every quantity that matters (sensing, communication, geometry, failures) must be
parameterised and reproducible from a config file, never hard-coded.

## Structure
- `environment/`, the simulated world: targets/sources, obstacles, disturbances, ground truth, scenario generation.
- `dynamics/`, agent dynamics (start idealised, add realism progressively; keep the two separate).
- `sensing/`, sensor models, one module per modality.
- `communication/`, controllable bandwidth, latency, packet loss, topology, message size.
- `estimation/`, the estimator implementation, independent from control algorithms.
- `scenarios/`, standardised, reproducible scenarios (baseline, degraded sensing/comms, agent failure, etc.).
- `configs/`, YAML configs for every experimental sweep; never hard-code parameters in scripts.
- `runners/`, scripts that execute experiments (`run_single.py`, `run_batch.py`, `run_sweep.py`, `run_scaling.py`).
- `validation/`, tests that the simulator itself behaves correctly. **A simulator producing
  graphs is not evidence if the simulator has not been validated first.**

## Before running any real experiment
1. Validate every module in `validation/` (sensor model, communication model, dynamics, estimator,
   ground truth, random-seed reproducibility, boundary conditions).
2. Only then run pilot experiments (`experiments/pilot/`).
