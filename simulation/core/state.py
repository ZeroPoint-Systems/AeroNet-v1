"""Immutable two dimensional state representation.

This module intentionally contains no physics and no estimation logic. It
defines only the geometric primitive used throughout the simulator to
represent a position in the plane.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class State2D:
    """An immutable point in two dimensional space.

    Both coordinates must be finite. NaN and infinity are rejected at
    construction time rather than allowed to propagate silently into later
    calculations.
    """

    x: float
    y: float

    def __post_init__(self) -> None:
        for name, value in (("x", self.x), ("y", self.y)):
            if not math.isfinite(value):
                raise ValueError(
                    f"State2D.{name} must be finite, got {value!r}"
                )

    def as_array(self) -> np.ndarray:
        """Return the state as a two element NumPy array, in order x, y."""
        return np.array([self.x, self.y], dtype=float)

    def distance_to(self, other: "State2D") -> float:
        """Euclidean distance to another State2D."""
        return math.sqrt(self.squared_distance_to(other))

    def squared_distance_to(self, other: "State2D") -> float:
        """Squared Euclidean distance to another State2D.

        Provided separately from distance_to because several downstream
        calculations, such as comparing a distance against a squared
        threshold, do not need the square root and should not pay for it.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    @staticmethod
    def from_array(values: np.ndarray) -> "State2D":
        """Construct a State2D from a two element array like object."""
        if len(values) != 2:
            raise ValueError(
                f"expected exactly two values, got {len(values)}"
            )
        return State2D(x=float(values[0]), y=float(values[1]))
