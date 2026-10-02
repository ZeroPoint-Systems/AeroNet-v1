from experiments.runners.run_batch import expand_grid, stable_seed


def test_grid_expansion():
    grid = {
        "a": [1, 2],
        "b": [10, 20],
    }

    runs = list(expand_grid(grid))

    assert len(runs) == 4
    assert {"a": 1, "b": 10} in runs
    assert {"a": 2, "b": 20} in runs


def test_seed_is_deterministic():
    assert stable_seed(123, 0) == stable_seed(123, 0)
    assert stable_seed(123, 0) != stable_seed(123, 1)
