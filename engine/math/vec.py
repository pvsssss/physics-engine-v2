from __future__ import annotations
from typing import Tuple
import math

EPSILON = 1e-8


class Vec2:
    __slots__ = ("x", "y")
    x: float
    y: float

    # initialising the 2d vector
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)

    # mainly for debugging
    def __repr__(self) -> str:
        return f"Vec2(x={self.x:.4f}, y={self.y:.4f})"

    def copy(self) -> Vec2:
        return Vec2(self.x, self.y)

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    # basic arithmetic operations
    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __neg__(self) -> Vec2:
        return Vec2(-self.x, -self.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vec2:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vec2:
        if scalar == 0.0:
            raise ZeroDivisionError("Division by zero in Vec2")
        inv = 1.0 / scalar
        return Vec2(self.x * inv, self.y * inv)

    # basic lengt calculations
    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def length_squared(self) -> float:
        """
        Squared magnitude.
        Used when comparing lengths without a sqrt.
        """
        return self.x * self.x + self.y * self.y

    def normalized(self) -> Vec2:
        mag = self.length()
        if mag < EPSILON:  # Use threshold instead of exact zero
            return Vec2(0.0, 0.0)
        return self / mag

    # using epsilon
    def is_zero(self, eps: float = 1e-8) -> bool:
        return abs(self.x) < eps and abs(self.y) < eps

    # dot and cross products
    def dot(self, other: Vec2) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vec2) -> float:
        return self.x * other.y - self.y * other.x

    # projections and perpendicular vectors
    def perpendicular(self) -> Vec2:
        """
        Returns a vector rotated 90 degrees counter-clockwise.
        """
        return Vec2(-self.y, self.x)

    def project_onto(self, axis: Vec2) -> Vec2:
        """
        Projects this vector onto another vector (axis).
        """
        axis_len_sq = axis.length_squared()
        if axis_len_sq == 0.0:
            return Vec2(0.0, 0.0)

        scale = self.dot(axis) / axis_len_sq
        return axis * scale

    def add_ip(self, other: Vec2) -> None:
        self.x += other.x
        self.y += other.y

    def sub_ip(self, other: Vec2) -> None:
        self.x -= other.x
        self.y -= other.y

    def mul_ip(self, scalar: float) -> None:
        self.x *= scalar
        self.y *= scalar

    def set(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    def clamp_length(self, max_len: float) -> None:
        mag_sq = self.length_squared()
        if mag_sq > max_len * max_len:
            mag = math.sqrt(mag_sq)
            scale = max_len / mag
            self.x *= scale
            self.y *= scale

    # static helper functions
    @staticmethod
    def distance(a: Vec2, b: Vec2) -> float:
        return (a - b).length()

    @staticmethod
    def lerp(a: Vec2, b: Vec2, t: float) -> Vec2:
        """
        Linear interpolation between vectors.
        """
        return a + (b - a) * t

    @staticmethod
    def distance_squared(a: Vec2, b: Vec2) -> float:
        """
        Calculates distance between two vectors
        """
        dx = a.x - b.x
        dy = a.y - b.y
        return dx * dx + dy * dy
