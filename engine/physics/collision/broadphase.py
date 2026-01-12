from __future__ import annotations
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import math

from engine.math.aabb import AABB
from engine.physics.particle import Particle


CellCoord = Tuple[int, int]
ParticlePair = Tuple[Particle, Particle]


class SpatialHashGrid:
    """
    Spatial hash grid for broadphase collision detection.
    """

    __slots__ = ("cell_size", "inv_cell_size", "cells")

    def __init__(self, cell_size: float) -> None:
        if cell_size <= 0.0:
            raise ValueError("cell_size must be positive")

        self.cell_size: float = cell_size
        self.inv_cell_size: float = 1.0 / cell_size

        # maps cell coordinate -> list of particles
        self.cells: Dict[CellCoord, List[Particle]] = defaultdict(list)

    def clear(self) -> None:
        self.cells.clear()

    def _hash_coord(self, x: float, y: float) -> CellCoord:
        return (
            int(math.floor(x * self.inv_cell_size)),
            int(math.floor(y * self.inv_cell_size)),
        )

    def _cells_for_aabb(self, aabb: AABB) -> List[CellCoord]:
        min_x, min_y = self._hash_coord(aabb.min.x, aabb.min.y)
        max_x, max_y = self._hash_coord(aabb.max.x, aabb.max.y)

        coords: List[CellCoord] = []

        for cx in range(min_x, max_x + 1):
            for cy in range(min_y, max_y + 1):
                coords.append((cx, cy))

        return coords

    def insert(self, particle: Particle) -> None:
        """
        Inserts a particle into all grid cells overlapped by its AABB.
        """

        aabb = AABB(
            particle.position - particle.radius_vec,
            particle.position + particle.radius_vec,
        )

        for coord in self._cells_for_aabb(aabb):
            self.cells[coord].append(particle)

    def compute_pairs(self) -> List[ParticlePair]:
        """
        Returns a list of unique particle pairs that may collide.
        """

        pairs: Set[Tuple[int, int]] = set()
        result: List[ParticlePair] = []

        for cell_particles in self.cells.values():
            count = len(cell_particles)
            if count < 2:
                continue

            for i in range(count):
                a = cell_particles[i]
                for j in range(i + 1, count):
                    b = cell_particles[j]

                    # enforce uniqueness using id
                    key = (id(a), id(b)) if id(a) < id(b) else (id(b), id(a))

                    if key in pairs:
                        continue

                    pairs.add(key)
                    result.append((a, b))

        return result
