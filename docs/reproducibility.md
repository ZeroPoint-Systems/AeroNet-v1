Reproducibility

What is guaranteed now

Given the same configuration file and the same seed, run_simulation() in experiments/runners/run_experiment.py produces a bitwise identical trajectory. This is achieved by deriving every random stream in a run, agent spawn positions, sensing noise, and communication packet loss, from a single np.random.SeedSequence built from the seed recorded in the configuration, using SeedSequence.spawn() to create independent, reproducible child generators rather than reusing one generator across unrelated purposes. This is checked directly by tests/reproducibility/test_determinism.py, and is the single most important guarantee in the codebase; if it is ever broken, every experiment result produced since is suspect.

Every completed experiment run writes, into experiments/raw/<experiment_id>/: a copy of the exact configuration file used, config.yaml; a metadata.json recording the UTC timestamp, the git commit, the software version, the Python version, the platform, and the NumPy version; the full per agent trajectory, trajectory.csv; summary metrics, metrics.csv; and a manifest.json tying the experiment id, git commit, seed, configuration filename, hardware version, software version and communication statistics together. A copy of the manifest is also written to experiments/manifests/<experiment_id>.json.

Raw output is treated as write once: run() raises FileExistsError if the experiment id has already produced output, so a result is never silently overwritten. This is checked by tests/reproducibility/test_determinism.py.

Git commit tracking

_git_commit(), in experiments/runners/run_experiment.py, records the actual output of git rev-parse HEAD, run against the repository root, and writes the literal string unknown if the repository has no git history, for example immediately after this codebase is unpacked and before it has been committed anywhere. It never fabricates a commit hash. Once this repository is added to version control, every experiment run from that point onward will carry a real, checkable commit reference. Running the pilot experiment before committing the code will correctly show unknown; this is expected behaviour, not a bug, and is worth doing again once the repository has its own git history, so that the recorded pilot run has a real commit to point to.

What reproducibility does not yet cover

Cross machine reproducibility, meaning identical floating point results on a different operating system, processor architecture, or NumPy build, has not been tested. Standard IEEE 754 floating point arithmetic and NumPy's documented random number generation should make this likely for the operations used here, but it is not yet confirmed and should not be assumed.

Environment reproducibility beyond the recorded NumPy and Python versions, meaning a full dependency lock file, is not yet in place. environment.yml and requirements.txt list the required packages, but not pinned exact versions; pinning exact versions is a reasonable next step once the dependency set has stabilised beyond this first sprint.

Independent reproduction, meaning someone other than the original author cloning the repository, installing the environment, and reproducing a specific result without further help, has not yet been attempted. This is the actual target described in research/specification_questionnaire.md, Part XXXVI, and remains unverified until it is tried.

How to reproduce the pilot result

Install the dependencies listed in requirements.txt or environment.yml. Run python -m experiments.runners.run_experiment --config experiments/configs/pilot_001.yaml from the repository root. The output will appear in experiments/raw/pilot_001, alongside a copy of the manifest in experiments/manifests/pilot_001.json. Running the same command a second time without removing that output directory will raise FileExistsError by design.
