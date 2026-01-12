from __future__ import annotations
from abc import ABC, abstractmethod

from engine.math.vec import Vec2
from engine.physics.particle import Particle


class Force(ABC):
    """
    Abstract base class for all forces.

    A force:
    - reads particle state
    - writes to particle.force
    - never integrates or moves particles directly
    """

    @abstractmethod
    def apply(self, particle: Particle, dt: float) -> None:
        pass


class Gravity(Force):
    """
    Uniform gravity applied to all particles.
    """

    __slots__ = ("g",)

    def __init__(self, gravity: Vec2) -> None:
        self.g = gravity

    def apply(self, particle: Particle, dt: float) -> None:
        if particle.inv_mass == 0.0:
            return

        # F = m * g
        particle.force.add_ip(self.g * particle.mass)


class LinearDrag(Force):
    """
    Velocity-proportional drag force.
    """

    __slots__ = ("k",)

    def __init__(self, coefficient: float) -> None:
        self.k = float(coefficient)

    def apply(self, particle: Particle, dt: float) -> None:
        # F = -k * v
        particle.force.add_ip(-self.k * particle.velocity)


class PointForce(Force):
    """
    Base class for forces with a position in space.
    """

    __slots__ = ("position",)

    def __init__(self, position: Vec2) -> None:
        self.position = position


class RadialForce(PointForce):
    """
    Radial inverse-square force.
    THIS FORCE IS A BIT BUGGY RIGHT NOW AND IS NOT INTENDED FOR US
    Can represent:
    - gravity wells
    - electrostatic forces
    - explosions (repulsive)
    """

    __slots__ = ("strength", "min_radius")

    def __init__(
        self,
        position: Vec2,
        strength: float,
        min_radius: float = 0.0001,
    ) -> None:
        super().__init__(position)
        self.strength = float(strength)
        self.min_radius = float(min_radius)

    def apply(self, particle: Particle, dt: float) -> None:
        delta = self.position - particle.position
        dist_sq = delta.length_squared()
        dist_sq = max(dist_sq, self.min_radius * self.min_radius)
        direction = delta.normalized()
        force_mag = self.strength / dist_sq

        particle.force.add_ip(direction * force_mag)
