from __future__ import annotations
from abc import ABC, abstractmethod
from engine.physics.particle import Particle


class Constraint(ABC):
    """
    Base class for particle constraints.
    Constraints maintain relationships between particles.
    """

    @abstractmethod
    def solve(self, dt: float = 1.0 / 60.0) -> None:
        """
        Solve the constraint by adjusting particle positions/velocities.
        """
        pass

    @abstractmethod
    def get_particles(self) -> tuple[Particle, ...]:
        """
        Returns the particles involved in this constraint.
        """
        pass
