from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

from engine.math.vec import Vec2


@dataclass
class AABB:
    """
    Axis-Aligned Bounding Box.
    Represents a rectangle aligned with the world axes.
    Used for broadphase collision detection.
    """

    min: Vec2  # bottom left corner
    max: Vec2  # top right corner

    def __post_init__(self) -> None:
        if self.min.x > self.max.x or self.min.y > self.max.y:
            raise ValueError("Invalid AABB: min must be <= max")

    def overlaps(self, other: AABB) -> bool:
        """
        Returns True if this AABB overlaps another AABB.
        """

        # Separation along x-axis
        if self.max.x < other.min.x or self.min.x > other.max.x:
            return False

        # Separation along y-axis
        if self.max.y < other.min.y or self.min.y > other.max.y:
            return False

        return True

    def expand(self, amount: float) -> AABB:
        """
        Returns a new AABB expanded equally in all directions.
        """
        return AABB(
            Vec2(self.min.x - amount, self.min.y - amount),
            Vec2(self.max.x + amount, self.max.y + amount),
        )

    @staticmethod
    def from_points(points: Iterable[Vec2]) -> AABB:
        """
        Creates an AABB that encloses all given points.
        """

        points = list(points)
        if not points:
            raise ValueError("Cannot create AABB from empty point list")

        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)

        return AABB(
            Vec2(min_x, min_y),
            Vec2(max_x, max_y),
        )

    @property
    def width(self) -> float:
        return self.max.x - self.min.x

    @property
    def height(self) -> float:
        return self.max.y - self.min.y

    @property
    def center(self) -> Vec2:
        return Vec2(
            (self.min.x + self.max.x) * 0.5,
            (self.min.y + self.max.y) * 0.5,
        )

    def contains_point(self, p: Vec2) -> bool:
        return self.min.x <= p.x <= self.max.x and self.min.y <= p.y <= self.max.y
