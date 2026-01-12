from __future__ import annotations
from dataclasses import dataclass, field

from engine.math.vec import Vec2


@dataclass
class Particle:
    """
    Live particle instance.

    Represents a point mass with linear motion only.
    No rotation, no angular velocity.
    """

    position: Vec2
    velocity: Vec2
    radius: float
    mass: float

    friction: float = 0.3
    restitution: float = 0.4
    damping: float = 0.0
    sleep_threshold: float = 0.05
    alive: bool = True

    force: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    inv_mass: float = field(init=False)
    sleeping: bool = field(default=False, init=False)
    sleep_timer: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("Particle mass must be positive")

        self.inv_mass = 1.0 / self.mass

    def kill(self) -> None:
        """Marks the particle as dead."""
        self.alive = False

    def is_alive(self) -> bool:
        return self.alive

    def clear_force(self) -> None:
        """Clears accumulated force."""
        self.force = Vec2(0.0, 0.0)

    @property
    def radius_vec(self) -> Vec2:
        return Vec2(self.radius, self.radius)
