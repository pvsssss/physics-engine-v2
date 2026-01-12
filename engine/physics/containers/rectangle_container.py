from __future__ import annotations
from typing import List

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.containers.base import Container
from engine.physics.static_body import StaticBody
from engine.physics.contact import Contact


class RectangleContainer(Container):
    """
    Axis-aligned rectangular container.
    Particles are constrained INSIDE the rectangle.
    """

    def __init__(self, x: float, y: float, width: float, height: float):
        self.min = Vec2(x, y)
        self.max = Vec2(x + width, y + height)

    def generate_contacts(self, p: Particle) -> List[Contact]:
        contacts: List[Contact] = []
        r = p.radius

        # Left wall (particle penetrating from right)
        if p.position.x - r < self.min.x:
            penetration = self.min.x - (p.position.x - r)
            contacts.append(
                Contact(
                    a=p,
                    b=StaticBody(),
                    normal=Vec2(-1.0, 0.0),  # Points LEFT (from particle to wall)
                    penetration=penetration,
                    contact_points=[Vec2(self.min.x + r, p.position.y)],
                )
            )

        # Right wall (particle penetrating from left)
        if p.position.x + r > self.max.x:
            penetration = (p.position.x + r) - self.max.x
            contacts.append(
                Contact(
                    a=p,
                    b=StaticBody(),
                    normal=Vec2(1.0, 0.0),  # Points RIGHT (from particle to wall)
                    penetration=penetration,
                    contact_points=[Vec2(self.max.x - r, p.position.y)],
                )
            )

        # Top wall (particle penetrating from below)
        if p.position.y - r < self.min.y:
            penetration = self.min.y - (p.position.y - r)
            contacts.append(
                Contact(
                    a=p,
                    b=StaticBody(),
                    normal=Vec2(0.0, -1.0),  # Points UP (from particle to wall)
                    penetration=penetration,
                    contact_points=[Vec2(p.position.x, self.min.y + r)],
                )
            )

        # Bottom wall (particle penetrating from above)
        if p.position.y + r > self.max.y:
            penetration = (p.position.y + r) - self.max.y
            contacts.append(
                Contact(
                    a=p,
                    b=StaticBody(),
                    normal=Vec2(0.0, 1.0),  # Points DOWN (from particle to wall)
                    penetration=penetration,
                    contact_points=[Vec2(p.position.x, self.max.y - r)],
                )
            )

        return contacts
