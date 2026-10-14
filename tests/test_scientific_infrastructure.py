from experiments.scientific.metrics import (
    delivery_rate,
    failure_rate,
    median,
    percentile,
    rmse,
)

from experiments.scientific.protocol import (
    Condition,
    build_protocol,
    derive_seed,
)

from experiments.scientific.statistics import (
    bootstrap_mean_ci,
    cohens_d,
)


def test_rmse():
    assert rmse([3.0, 4.0]) == 3.5355339059327378


def test_median():
    assert median([1.0, 4.0, 2.0]) == 2.0
    assert median([1.0, 4.0, 2.0, 8.0]) == 3.0


def test_percentile():
    assert percentile([1.0, 2.0, 3.0, 4.0], 50.0) == 2.5


def test_delivery_rate():
    assert delivery_rate(100, 80) == 0.8


def test_failure_rate():
    assert failure_rate([1.0, 2.0, 3.0], 2.0) == 1.0 / 3.0


def test_seed_is_deterministic():
    first = derive_seed(123, "abc", 1, "aeronet")
    second = derive_seed(123, "abc", 1, "aeronet")
    assert first == second


def test_different_experiments_get_different_seeds():
    first = derive_seed(123, "abc", 1, "aeronet")
    second = derive_seed(123, "abc", 2, "aeronet")
    assert first != second


def test_protocol_contains_expected_replicates():
    protocol = build_protocol(
        measurement_noise=[1.0],
        communication_range=[25.0],
        packet_loss_probability=[0.0],
        latency=[0.0],
        number_of_agents=[4],
        replicates=3,
        base_seed=123,
        baselines=["aeronet", "centralised"],
    )

    assert len(protocol) == 6
    assert len({item.seed for item in protocol}) == 6


def test_condition_identifier_is_deterministic():
    condition = Condition(
        measurement_noise=1.0,
        communication_range=25.0,
        packet_loss_probability=0.05,
        latency=0.1,
    )

    assert condition.condition_id() == condition.condition_id()


def test_bootstrap_ci_is_finite():
    low, high = bootstrap_mean_ci([1.0, 2.0, 3.0, 4.0])
    assert low <= 2.5 <= high


def test_cohens_d_zero_for_identical_samples():
    assert cohens_d(
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0],
    ) == 0.0
