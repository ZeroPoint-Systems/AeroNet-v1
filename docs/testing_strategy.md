Testing strategy

Test layout

Tests live under tests/, in a directory structure mirroring simulation/: tests/simulation, tests/sensing, tests/communication, tests/estimation, tests/metrics, tests/reproducibility. Every test file is an ordinary pytest style module: plain functions named test_something, using assert and pytest.raises. pyproject.toml sets testpaths to tests, so running pytest from the repository root discovers all of them.

conftest.py, at the repository root, adds the repository root to sys.path, so that test modules can write import simulation.core.state and import analysis.metrics.estimation_error regardless of which directory pytest is invoked from.

tests/run_all.py is a dependency free fallback. It discovers every tests/**/test_*.py file, imports it, and calls every top level test_ function that takes no arguments, without needing pytest itself installed. It exists only for environments where installing pytest is not possible; wherever pytest is available, use pytest, since it also runs the tests that need fixtures such as tmp_path, which run_all.py deliberately skips.

Categories of test

Unit tests check a single function or class in isolation: for example, tests/simulation/test_state.py checks State2D's distance calculation against a known 3, 4, 5 triangle, and tests/communication/test_packet_loss.py checks that a loss probability of exactly 0 or exactly 1 behaves as expected on every trial.

Integration tests check components interacting: tests/communication/test_channel.py builds a real CommunicationGraph and sends a packet through a real Channel, checking that it is not delivered before its scheduled time and is not sent at all across a missing edge.

Scientific validation tests check that an implementation reproduces known mathematical behaviour: tests/estimation/test_reference_kalman.py includes a fully worked scalar Kalman update, x0 = 0, P0 = 1, R = 1, z = 10, giving a posterior mean of 5 and a posterior covariance of 0.5, checked against the implementation's actual output, not just checked for a plausible shape.

Reproducibility tests, in tests/reproducibility, are the two most important test files in the repository. test_determinism.py runs the same configuration twice under the same seed and requires the resulting trajectories to be exactly equal, then runs it again under a different seed and requires the trajectories to differ. test_information_isolation.py constructs a world and swarm, then changes the true target state directly, and requires that no agent's estimate changes as a result, since the only permitted route from ground truth to an agent's estimate is an explicit Observation.

What is covered now

Every module written in this sprint has at least one test file: simulation/core/state.py, simulation/core/time.py, simulation/core/swarm.py, simulation/core/agent.py, simulation/sensing/noise.py, simulation/sensing/observation_model.py, simulation/communication/packet.py, simulation/communication/graph.py, simulation/communication/packet_loss.py, simulation/communication/latency.py, simulation/communication/channel.py, simulation/estimation/reference_kalman.py, simulation/estimation/covariance_intersection.py, analysis/metrics/estimation_error.py, analysis/metrics/covariance.py, analysis/metrics/entropy.py, and the full pipeline through experiments/runners/config.py and experiments/runners/run_experiment.py.

What is not covered yet

simulation/core/world.py has no dedicated test file; it is exercised indirectly through experiments/runners/run_experiment.py and the reproducibility tests, but does not yet have a direct unit test of its own. There is no test yet for the CLI entry point in run_experiment.py's main function, only for the run() function it calls. There is no performance or scaling test yet, since no experiment beyond the pilot configuration has been run. None of this is a gap that has been decided to leave; it is simply not yet done, and should be closed before the pilot experiment's results are treated as validated infrastructure rather than a first working version.

Verification carried out for this sprint

Every test file was executed against the implementation before delivery, using pytest style assertions. Where pytest itself was not installable in the environment used to write this code, a local, temporary stand in for pytest.raises was used purely to check correctness, and was not included in the delivered repository; the test files themselves are unmodified, ordinary pytest tests. All 79 parameterless tests passed, and the two tests requiring pytest's tmp_path fixture were separately verified by hand, including that rerunning an existing experiment id correctly raises FileExistsError.
