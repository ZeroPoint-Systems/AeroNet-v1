"""The most important test in the repository.

If this test ever fails, something in the codebase has started reading
from a global, unseeded source of randomness, and every experiment result
produced since is suspect until the cause is found and fixed.
"""

import shutil
from dataclasses import replace
from pathlib import Path

from experiments.runners.config import load_config
from experiments.runners.run_experiment import run, run_simulation

REPO_ROOT = Path(__file__).resolve().parents[2]
PILOT_CONFIG_PATH = REPO_ROOT / "experiments" / "configs" / "pilot_001.yaml"


def test_same_seed_produces_bitwise_identical_trajectory():
    config = load_config(str(PILOT_CONFIG_PATH))
    result_a = run_simulation(config)
    result_b = run_simulation(config)
    assert result_a["trajectory"] == result_b["trajectory"]
    assert result_a["communication_stats"] == result_b["communication_stats"]


def test_different_seed_produces_a_different_trajectory():
    config = load_config(str(PILOT_CONFIG_PATH))
    other_config = replace(config, experiment=replace(config.experiment, seed=config.experiment.seed + 1))
    result_a = run_simulation(config)
    result_b = run_simulation(other_config)
    assert result_a["trajectory"] != result_b["trajectory"]


def test_full_run_is_reproducible_from_its_own_written_config(tmp_path):
    output_dir = run(str(PILOT_CONFIG_PATH), output_root=tmp_path)
    assert (output_dir / "config.yaml").exists()
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "trajectory.csv").exists()
    assert (output_dir / "metrics.csv").exists()
    assert (output_dir / "manifest.json").exists()

    rerun_config_path = output_dir / "config.yaml"
    original_config = load_config(str(PILOT_CONFIG_PATH))
    rerun_config = load_config(str(rerun_config_path))
    assert run_simulation(original_config)["trajectory"] == run_simulation(rerun_config)["trajectory"]


def test_rerunning_the_same_experiment_id_is_refused(tmp_path):
    run(str(PILOT_CONFIG_PATH), output_root=tmp_path)
    try:
        run(str(PILOT_CONFIG_PATH), output_root=tmp_path)
        assert False, "expected FileExistsError when rerunning an existing experiment id"
    except FileExistsError:
        pass
