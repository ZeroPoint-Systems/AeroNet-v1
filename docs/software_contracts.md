Software contracts

This document states the rules the codebase is required to follow, and where each rule is currently enforced. Where enforcement does not yet exist, that is recorded honestly rather than implied.

No magic numbers in scientific code. Enforced by experiments/runners/config.py: every value that affects a result comes from a configuration file, checked at load time. Not yet enforced by any automated check across the whole codebase; a code review should look for hard coded constants outside tests.

No global mutable state. Enforced by design: every class in simulation/ holds its own state as instance attributes.

No hidden randomness. Enforced throughout simulation/sensing and simulation/communication: GaussianNoise, PacketLossModel and the observation model all require an explicit np.random.Generator at construction, never call the module level np.random functions. Checked directly by tests/reproducibility/test_determinism.py.

Every stochastic component receives an explicit RNG. Same as above. experiments/runners/run_experiment.py derives three independent child generators from a single seed using np.random.SeedSequence, one each for agent spawn positions, sensing noise, and the communication channel, so that a single recorded seed determines every random choice in a run.

Every experiment has an explicit configuration. Enforced by experiments/runners/config.py and experiments/configs/pilot_001.yaml.

Every result records the configuration and seed. Enforced by run(): the configuration file is copied into the output directory, and the seed is written into manifest.json.

Simulation code cannot silently access ground truth except through explicitly defined interfaces. Enforced by design in simulation/core/agent.py, and checked directly by tests/reproducibility/test_information_isolation.py.

Estimators cannot access future observations. Enforced by design: ReferenceKalmanFilter.update() only ever receives the single Observation passed to it, and the simulation loop only calls update() with the observation generated at the current timestep.

Agents cannot access another agent's private state unless it arrives through the communication layer. Enforced by design: Agent has no reference to Swarm or to other Agent instances; peer information can only arrive through Agent.receive_peer_estimate(), which is only ever called by the experiment runner after a packet has been delivered by Channel.

Baselines cannot call AeroNet internals. Not yet applicable: no baseline controller has been implemented yet. This contract will apply once algorithms/baselines and algorithms/aeronet exist.

Analysis cannot modify experimental results. Enforced by convention: analysis/metrics functions are pure and take copies of NumPy arrays; run_experiment.py treats experiments/raw as write once, refusing to rerun an existing experiment id.

Raw data are immutable. Enforced by run(): raises FileExistsError if the experiment id already has output on disk. Checked by tests/reproducibility/test_determinism.py.

Every experiment has a unique ID. Enforced by the same mechanism.

Every important function has tests. Enforced by the test suite in tests/, covering simulation/core, simulation/sensing, simulation/communication, simulation/estimation and analysis/metrics. See docs/testing_strategy.md for what is and is not yet covered.

Numerical assumptions are documented. Where a modelling choice is not yet settled by the literature or by experiment, it is marked ASSUMPTION in the relevant docstring, for example the fixed, position independent measurement model in simulation/sensing/observation_model.py, and the local only, no peer fusion behaviour of ReferenceKalmanFilter.

Scientific decisions are documented separately from implementation details. Scientific decisions live in research/ and theory/; implementation details live in this docs/ folder and in code comments. A change to a scientific decision, such as which information metric to use, should be made in theory/information_boundary.md first, and only then reflected in code.

If an assumption is not established by literature or experiment, label it ASSUMPTION, not FACT. See simulation/estimation/covariance_intersection.py for the clearest example: it is marked STATUS: LITERATURE-DEPENDENT and raises NotImplementedError rather than offering a plausible but unjustified fusion rule.

No machine learning or reinforcement learning at this stage. Not present anywhere in the codebase.

No realistic aircraft dynamics at this stage. Agents do not move in the current implementation; simulation/core/agent.py has a fixed position for the whole run.

No novel flight control system at this stage. Not applicable to the current software, which contains no hardware or flight control code; see hardware/flight_controller/README.md for the research level position on this.

Interfaces

Estimator, in simulation/estimation/base.py, is the contract every estimator must satisfy: predict, update, incorporate_peer_estimate, estimate, covariance. ObservationModel, in simulation/sensing/observation_model.py, is the contract every sensing model must satisfy: observe. Any new estimator or sensing model should implement these interfaces rather than being wired into the runner as a special case.
