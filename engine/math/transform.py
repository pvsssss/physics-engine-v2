from __future__ import annotations
from typing import Iterable, List

from engine.math.vec import Vec2
from engine.math.mat import Mat2


class Transform:
    __slots__ = ("position", "_angle", "_rotation", "_rotation_T")

    position: Vec2
    angle: float
    _rotation: Mat2
    _rotation_T: Mat2

    def __init__(self, position: Vec2 | None = None, angle: float = 0.0) -> None:
        """
        Takes in the position of the object and the angle it is rotated
        at. These are optional parameters and default to zero vec2 and
        0.0 respectively.
        """
        self.position = position.copy() if position else Vec2(0.0, 0.0)
        self.angle = float(angle)

        # cached rotation matrices
        self._rotation = Mat2.rotation(self.angle)
        self._rotation_T = self._rotation.transpose()

    def update_rotation(self) -> None:
        """
        Updates cached rotation matrices.
        Must be called whenever angle changes.
        """
        self._rotation = Mat2.rotation(self.angle)
        self._rotation_T = self._rotation.transpose()

    # transformations from world space to lcoal space
    def local_to_world(self, point: Vec2) -> Vec2:
        """
        Converts a point from local space to world space.
        """
        return self._rotation.mul_vec(point) + self.position

    def world_to_local(self, point: Vec2) -> Vec2:
        """
        Converts a point from world space to local space.
        """
        return self._rotation_T.mul_vec(point - self.position)

    def local_vector_to_world(self, vector: Vec2) -> Vec2:
        """
        Converts a direction vector from local to world space.
        (No translation applied.)
        """
        return self._rotation.mul_vec(vector)

    def world_vector_to_local(self, vector: Vec2) -> Vec2:
        """
        Converts a direction vector from world to local space.
        """
        return self._rotation_T.mul_vec(vector)

    def transform_points(self, points: Iterable[Vec2]) -> List[Vec2]:
        """
        Transforms multiple local-space points to world space.
        """
        return [self.local_to_world(p) for p in points]

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = float(value)
        self._rotation = Mat2.rotation(self._angle)
        self._rotation_T = self._rotation.transpose()

    def translate(self, delta: Vec2) -> None:
        self.position.add_ip(delta)

    def set_angle(self, angle: float) -> None:
        self.angle = float(angle)
        self.update_rotation()

    def copy(self) -> Transform:
        return Transform(self.position.copy(), self.angle)
