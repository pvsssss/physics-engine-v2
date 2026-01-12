from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from engine.physics.contact import Contact
from engine.physics.particle import Particle


class Container(ABC):
    """
    Base class for static collision containers.
    """

    @abstractmethod
    def generate_contacts(self, particle: Particle) -> List[Contact]:
        """
        Returns a list of contacts between this container and the particle.
        """
        pass
