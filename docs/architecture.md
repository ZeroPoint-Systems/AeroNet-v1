Architecture

This document describes how the code in this repository is put together, and why it is split the way it is. It sits between the research documents in research/ and theory/, which say what is being investigated, and the actual implementation in simulation/, algorithms/, experiments/ and analysis/, which carries that investigation out.

Overall flow

The intended path from question to result is:

scientific question, in research/
then hypotheses and theory, in research/ and theory/
then an experimental protocol, in research/experimental_protocol.md
then software contracts, in this docs/ folder
then the simulator and baselines, in simulation/ and algorithms/
then experiments, in experiments/
then analysis, in analysis/
then falsification, in research/falsification_tests.md and experiments/adversarial/
then physical validation, in hardware/ and experiments/hardware_validation/
then the papers, in papers/

The software is not permitted to become the specification. If a scientific decision, such as which information metric to use or which fusion rule to trust, has not yet been settled in research/ or theory/, the code says so explicitly, usually by raising NotImplementedError with an explanation, rather than quietly picking something reasonable and moving on.

The simulation package

simulation/core holds the objects with no scientific content of their own: a typed 2D state, a deterministic clock, an agent, a swarm, and a world. None of these decide how estimation, sensing or communication behave; they only hold state and enforce basic invariants such as unique agent IDs and finite coordinates.

simulation/sensing holds the observation model and noise model. The current model is z = x + v, a deliberately simple baseline that does not depend on agent position. A geometry dependent model is a documented future step, not yet built, since introducing it before the simple case is validated would make it impossible to tell which change caused any observed effect.

simulation/communication holds the packet, the communication graph, the channel, and the packet loss and latency models. Agents never call one another directly. Every message goes through a Packet, and every packet is subject to the graph, then packet loss, then latency, inside Channel. This separation is what allows communication conditions to be varied experimentally without touching agent code.

simulation/estimation holds the Estimator interface and its implementations. ReferenceKalmanFilter is a local only estimator with an analytically checkable behaviour, used to validate the rest of the pipeline. CovarianceIntersectionEstimator is a documented placeholder: distributed estimation with correlated peer estimates is an open, literature dependent decision, not something to be resolved by picking the easiest fusion rule.

The experiments package

experiments/runners/config.py loads and validates a YAML configuration file, and refuses to proceed if any required field is missing or out of range. experiments/runners/run_experiment.py wires the world, swarm, sensing, communication and estimation layers together according to that configuration, runs the simulation loop, and writes a complete experiment record: the configuration, metadata about the software and environment, the full per agent trajectory, summary metrics, and a manifest.

The analysis package

analysis/metrics holds pure functions only: position error, squared error, RMSE, covariance trace, covariance determinant, and Gaussian entropy. None of these is yet the chosen primary information metric for the boundary; that choice belongs to theory/information_boundary.md and analysis/boundary_estimation, once the literature review is complete.

Why the separation matters

Every one of these boundaries exists for a specific reason tied to the research question itself. If sensing, communication and estimation code were tangled together, it would be impossible to change one information condition without risking a change to another, and any observed effect on collective estimation could not be attributed to a single cause. The architecture is designed so that, later, an experiment can vary exactly one factor, such as packet loss, while holding everything else fixed, with the code itself enforcing that separation rather than relying on discipline alone.
