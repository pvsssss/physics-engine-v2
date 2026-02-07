from __future__ import annotations
from dataclasses import dataclass
from typing import List

from engine.math.vec import Vec2
from engine.physics.particle import Particle


@dataclass
class Contact:
    """
    dataclass for a particle data-object
    """

    a: Particle  # particle referrences
    b: Particle
    normal: Vec2  # Unit vector pointing from A to B
    penetration: float  # Overlap depth (> 0)
    contact_points: List[Vec2]

    def swap(self) -> None:
        self.a, self.b = self.b, self.a
        self.normal = -self.normal
