Experiment lifecycle

This describes what actually happens, step by step, when an experiment is run with the current codebase, and what is deliberately not yet handled.

1. A configuration file is written under experiments/configs, following the fields set out in experiments/runners/config.py: experiment id and seed, simulation dt and duration, target position, swarm size and spawn radius, sensing measurement noise, communication range, packet loss probability, latency and whether peer fusion is enabled, and the estimation method with its initial covariance and process noise.

2. experiments/runners/config.py loads the file and validates every field, raising ConfigError with a specific message if a field is missing or out of range, including a check that peer fusion is not requested for an estimator that does not implement it.

3. experiments/runners/run_experiment.py builds a World and a Swarm from the configuration, spawning each agent at a random position drawn from the seeded RNG, and gives each agent its own ReferenceKalmanFilter with an uninformative prior, not the true target location.

4. The simulation loop runs for the configured number of steps. At each step, every available agent predicts, then receives one observation from the sensing model, then updates its local estimate from that observation. The communication graph is rebuilt from current agent positions, every agent attempts to send its current estimate to its neighbours, the channel applies packet loss and latency, and any packets that arrive at the current time are collected. If peer fusion is enabled in the configuration, delivered estimates are passed to the receiving agent's estimator; otherwise they are delivered but not incorporated, so the communication pipeline is still fully exercised. Every agent's position error and covariance trace are recorded for that step.

5. Once the loop finishes, per agent RMSE and final covariance trace are computed from the recorded trajectory.

6. The complete record is written to experiments/raw/<experiment_id>: the configuration file, run metadata, the full trajectory, the summary metrics, and a manifest, with a copy of the manifest also placed in experiments/manifests.

7. If the experiment id has already been used, step 6 refuses to run at all, and raises FileExistsError before any output is written for the new attempt.

What is not yet handled

There is currently no graceful handling of a mid run failure. If an exception occurs during the simulation loop, for example from a malformed payload or a numerical error, it propagates up and no output directory is created for that attempt, rather than a partially written or explicitly marked failed record being kept. Rule 7 in CONTRIBUTING.md requires that failed experiments be retained, not deleted; the current behaviour satisfies that only in the narrow sense that nothing is silently discarded, since nothing is written in the first place. A proper failed status, written to a manifest even when a run does not complete, is a reasonable next step and is not yet built.

There is no experiment queue or batch runner yet. experiments/runners/run_experiment.py runs exactly one configuration per invocation. The parameter sweep experiments described in research/experimental_protocol.md, sections such as Experimental levels, will need a batch runner that calls run() once per configuration, which does not exist yet.

There is no automatic exclusion handling. research/experimental_protocol.md requires exclusion criteria to be fixed before the main campaign and applied mechanically; no such mechanism has been built, since no exclusion criteria have been fixed yet.

Agents do not move. The lifecycle above has no step corresponding to reconfiguration or geometry change, since simulation/core/agent.py fixes an agent's position for the whole run. This is intentional for the current sprint, consistent with CONTRIBUTING.md's build order, which places movement and geometry after the static phenomenon has been established, not before.
