from __future__ import annotations

import math
from typing import Iterable


def _finite(values: Iterable[float]) -> list[float]:
    return [
        float(value)
        for value in values
        if value is not None and math.isfinite(float(value))
    ]


def rmse(values: Iterable[float]) -> float:
    data = _finite(values)

    if not data:
        return float("nan")

    return math.sqrt(
        sum(value * value for value in data) / len(data)
    )


def mean(values: Iterable[float]) -> float:
    data = _finite(values)

    if not data:
        return float("nan")

    return sum(data) / len(data)


def median(values: Iterable[float]) -> float:
    data = sorted(_finite(values))

    if not data:
        return float("nan")

    middle = len(data) // 2

    if len(data) % 2:
        return data[middle]

    return (data[middle - 1] + data[middle]) / 2.0


def percentile(values: Iterable[float], q: float) -> float:
    data = sorted(_finite(values))

    if not data:
        return float("nan")

    if not 0.0 <= q <= 100.0:
        raise ValueError("q must be between 0 and 100")

    if len(data) == 1:
        return data[0]

    position = (len(data) - 1) * q / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return data[lower]

    weight = position - lower

    return (
        data[lower] * (1.0 - weight)
        + data[upper] * weight
    )


def delivery_rate(
    packets_generated: int,
    packets_delivered: int,
) -> float:
    if packets_generated <= 0:
        return float("nan")

    return packets_delivered / packets_generated


def failure_rate(
    errors: Iterable[float],
    threshold: float,
) -> float:
    data = _finite(errors)

    if not data:
        return float("nan")

    return sum(error > threshold for error in data) / len(data)
