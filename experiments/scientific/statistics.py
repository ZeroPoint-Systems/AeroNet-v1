from __future__ import annotations

import math
import random
from typing import Iterable


def _finite(values: Iterable[float]) -> list[float]:
    return [
        float(value)
        for value in values
        if value is not None and math.isfinite(float(value))
    ]


def mean(values: Iterable[float]) -> float:
    data = _finite(values)

    if not data:
        return float("nan")

    return sum(data) / len(data)


def sample_std(values: Iterable[float]) -> float:
    data = _finite(values)

    if len(data) < 2:
        return float("nan")

    centre = mean(data)

    return math.sqrt(
        sum((value - centre) ** 2 for value in data)
        / (len(data) - 1)
    )


def bootstrap_mean_ci(
    values: Iterable[float],
    iterations: int = 5000,
    confidence: float = 0.95,
    seed: int = 20261007,
) -> tuple[float, float]:
    data = _finite(values)

    if not data:
        return float("nan"), float("nan")

    if len(data) == 1:
        return data[0], data[0]

    rng = random.Random(seed)
    n = len(data)
    estimates = []

    for _ in range(iterations):
        sample = [data[rng.randrange(n)] for _ in range(n)]
        estimates.append(sum(sample) / n)

    estimates.sort()

    alpha = 1.0 - confidence

    low = int((alpha / 2.0) * len(estimates))
    high = int((1.0 - alpha / 2.0) * len(estimates))

    low = max(0, min(len(estimates) - 1, low))
    high = max(0, min(len(estimates) - 1, high))

    return estimates[low], estimates[high]


def cohens_d(
    a: Iterable[float],
    b: Iterable[float],
) -> float:
    x = _finite(a)
    y = _finite(b)

    if len(x) < 2 or len(y) < 2:
        return float("nan")

    mean_x = mean(x)
    mean_y = mean(y)

    var_x = sum(
        (value - mean_x) ** 2 for value in x
    ) / (len(x) - 1)

    var_y = sum(
        (value - mean_y) ** 2 for value in y
    ) / (len(y) - 1)

    pooled = math.sqrt(
        (
            (len(x) - 1) * var_x
            + (len(y) - 1) * var_y
        )
        / (len(x) + len(y) - 2)
    )

    if pooled == 0.0:
        return 0.0 if mean_x == mean_y else float("inf")

    return (mean_x - mean_y) / pooled
