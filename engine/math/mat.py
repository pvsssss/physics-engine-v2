from __future__ import annotations
from typing import Tuple
import math

from engine.math.vec import Vec2


class Mat2:

    __slots__ = ("m00", "m01", "m10", "m11")

    m00: float
    m01: float
    m10: float
    m11: float

    def __init__(self, m00: float, m01: float, m10: float, m11: float) -> None:
        self.m00 = float(m00)
        self.m01 = float(m01)
        self.m10 = float(m10)
        self.m11 = float(m11)

    # representation for debugging purposes
    def __repr__(self) -> str:
        return (
            f"Mat2([{self.m00:.4f}, {self.m01:.4f}], "
            f"[{self.m10:.4f}, {self.m11:.4f}])"
        )

    def to_tuple(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return (
            (self.m00, self.m01),
            (self.m10, self.m11),
        )

    # core functionallities and operations
    def mul_vec(self, v: Vec2) -> Vec2:
        """
        Matrix-vector multiplication.

        Used to rotate vectors and transform points.
        """
        return Vec2(
            self.m00 * v.x + self.m01 * v.y,
            self.m10 * v.x + self.m11 * v.y,
        )

    def mul_mat(self, other: Mat2) -> Mat2:
        """
        Matrix-matrix multiplication.

        Used when composing transformations.
        """
        return Mat2(
            self.m00 * other.m00 + self.m01 * other.m10,
            self.m00 * other.m01 + self.m01 * other.m11,
            self.m10 * other.m00 + self.m11 * other.m10,
            self.m10 * other.m01 + self.m11 * other.m11,
        )

    def transpose(self) -> Mat2:
        """
        Returns the transpose of the matrix.

        For rotation matrices, this is also the inverse.
        """
        return Mat2(self.m00, self.m10, self.m01, self.m11)

    def copy(self) -> Mat2:
        return Mat2(self.m00, self.m01, self.m10, self.m11)

    # basic helpful methods for matrices
    @staticmethod
    def identity() -> Mat2:
        """
        Identity matrix.
        """
        return Mat2(1.0, 0.0, 0.0, 1.0)

    @staticmethod
    def rotation(angle: float) -> Mat2:
        """
        Creates a rotation matrix for a given angle (radians).
        """
        c = math.cos(angle)
        s = math.sin(angle)

        return Mat2(c, -s, s, c)
