from __future__ import annotations
from typing import List

from engine.math.vec import Vec2
from engine.physics.contact import Contact
from engine.physics.particle import Particle
from engine.physics.containers.base import Container
from engine.physics.static_body import StaticBody


# Small epsilon for floating-point comparisons
EPSILON = 1e-8


class CircleContainer(Container):
    """
    Circular container.
    Particles are constrained INSIDE the circle.
    """

    def __init__(self, center: Vec2, radius: float):
        self.center = center
        self.radius = radius

    def generate_contacts(self, p: Particle) -> List[Contact]:
        delta = p.position - self.center
        dist = delta.length()

        # -------------------------------------------------
        # Handle particle at container center (edge case)
        # -------------------------------------------------
        if dist < EPSILON:
            # Particle spawned at exact center
            # Use arbitrary but deterministic normal
            normal = Vec2(1.0, 0.0)
            penetration = self.radius - p.radius
            contact_point = self.center + normal * (self.radius - p.radius)

            return [
                Contact(
                    a=p,
                    b=StaticBody(),
                    normal=normal,  # Push particle toward edge
                    penetration=penetration,
                    contact_points=[contact_point],
                )
            ]

        # -------------------------------------------------
        # Check if particle is outside container bounds
        # -------------------------------------------------
        if dist + p.radius <= self.radius:
            # Particle fully inside - no collision
            return []

        # -------------------------------------------------
        # Particle penetrating container boundary
        # -------------------------------------------------
        penetration = dist + p.radius - self.radius
        normal = delta / dist  # Unit vector from center outward

        # Contact point on container surface
        contact_point = self.center + normal * (self.radius - p.radius)

        return [
            Contact(
                a=p,
                b=StaticBody(),
                normal=normal,  # Points from particle toward wall (outward from center)
                penetration=penetration,
                contact_points=[contact_point],
            )
        ]
