from __future__ import annotations
from abc import ABC, abstractmethod
import math

from engine.math.vec import Vec2
from engine.math.aabb import AABB
from engine.physics.particle import Particle


class Force(ABC):
    """
    Abstract base class for force, not to be used in the actuall code/
    each child class required to have an apply method.
    """

    @abstractmethod
    def apply(self, particle: Particle, dt: float) -> None:
        pass


class Gravity(Force):
    """
    Gravity force class.
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


class WindForce(Force):
    """
    Constant wind force applied to all particles.
    Similar to gravity but typically used for horizontal forces.
    """

    __slots__ = ("force",)

    def __init__(self, force: Vec2) -> None:
        self.force = force

    def apply(self, particle: Particle, dt: float) -> None:
        if particle.inv_mass == 0.0:
            return

        particle.force.add_ip(self.force)


class RegionalForce(Force):
    """
    Abstract base class for forces that only apply within
    a specific region.

    subclasses required to implement a is in region method
    that returns a bool and a apply method that applies the force
    """

    @abstractmethod
    def is_in_region(self, particle: Particle) -> bool:
        """Returns True if particle is within the force's active region."""
        pass

    @abstractmethod
    def apply_regional_force(self, particle: Particle, dt: float) -> None:
        """Apply the force to a particle known to be in the region."""
        pass

    def apply(self, particle: Particle, dt: float) -> None:
        """Check region and apply force if particle is inside."""
        if self.is_in_region(particle):
            self.apply_regional_force(particle, dt)


class BuoyancyForce(RegionalForce):
    __slots__ = ("water_top", "water_bottom", "fluid_density", "gravity_mag")

    def __init__(
        self,
        water_top: float,
        water_bottom: float,
        fluid_density: float,
        gravity_magnitude: float,
    ) -> None:
        self.water_top = water_top
        self.water_bottom = water_bottom
        self.fluid_density = fluid_density
        self.gravity_mag = gravity_magnitude

    def is_in_region(self, particle: Particle) -> bool:
        particle_top = particle.position.y + particle.radius
        particle_bottom = particle.position.y - particle.radius
        # In bottom-left coords, top is greater than bottom
        return particle_bottom < self.water_top and particle_top > self.water_bottom

    def _calculate_submerged_fraction(self, particle: Particle) -> float:
        particle_top = particle.position.y + particle.radius
        particle_bottom = particle.position.y - particle.radius

        if particle_bottom >= self.water_top:
            return 0.0
        if particle_top <= self.water_top:
            return 1.0

        r = particle.radius
        h = self.water_top - particle_bottom
        h = max(0.0, min(h, 2.0 * r))

        d = r - h
        if abs(d) >= r:
            return 1.0 if d < 0 else 0.0

        theta = math.acos(d / r)
        segment_area = r * r * theta - d * math.sqrt(r * r - d * d)
        circle_area = math.pi * r * r
        return max(0.0, min(1.0, segment_area / circle_area))

    def apply_regional_force(self, particle: Particle, dt: float) -> None:
        if particle.inv_mass == 0.0:
            return
        submerged_fraction = self._calculate_submerged_fraction(particle)
        if submerged_fraction <= 0.0:
            return

        particle_area = math.pi * particle.radius * particle.radius
        submerged_area = particle_area * submerged_fraction
        buoyant_magnitude = self.fluid_density * self.gravity_mag * submerged_area

        # Apply upward force (Positive Y in bottom-left system)
        particle.force.y += buoyant_magnitude


class WaterDragForce(RegionalForce):
    __slots__ = ("water_top", "water_bottom", "fluid_density", "drag_coefficient")

    def __init__(
        self,
        water_top: float,
        water_bottom: float,
        fluid_density: float,
        drag_coefficient: float = 0.47,
    ) -> None:
        self.water_top = water_top
        self.water_bottom = water_bottom
        self.fluid_density = fluid_density
        self.drag_coefficient = drag_coefficient

    def is_in_region(self, particle: Particle) -> bool:
        particle_top = particle.position.y + particle.radius
        particle_bottom = particle.position.y - particle.radius
        return particle_bottom < self.water_top and particle_top > self.water_bottom

    def apply_regional_force(self, particle: Particle, dt: float) -> None:
        if particle.inv_mass == 0.0:
            return
        speed_sq = particle.velocity.length_squared()
        if speed_sq < 1e-6:
            return

        speed = math.sqrt(speed_sq)
        cross_section = 2.0 * particle.radius
        drag_magnitude = (
            0.5 * self.fluid_density * self.drag_coefficient * cross_section * speed_sq
        )

        drag_direction = particle.velocity / speed
        drag_force = drag_direction * (-drag_magnitude)
        particle.force.add_ip(drag_force)


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
