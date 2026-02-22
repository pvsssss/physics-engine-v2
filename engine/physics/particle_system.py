from __future__ import annotations

from typing import List

from engine.physics.particle import Particle
from engine.physics.forces import Force
from engine.physics.integrate import integrate_particle
from engine.physics.collision.broadphase import SpatialHashGrid
from engine.physics.collision.circle_circle import circle_circle
from engine.physics.solver import resolve_contact, positional_correction
from engine.physics.containers.base import Container
from engine.physics.constraints.base_constraint import Constraint


class ParticleSystem:
    """
    Updates particle objects using multiple different helper functions
    Use step() to step through one physics frame for all particles
    """

    __slots__ = (
        "particles",
        "global_forces",
        "local_forces",
        "paused",
        "broadphase",
        "solver_iterations",
        "containers",
        "constraints",
    )

    def __init__(self) -> None:
        self.particles: List[Particle] = []

        # Forces
        self.global_forces: List[Force] = []
        self.local_forces: List[Force] = []

        # State
        self.paused: bool = False
        self.broadphase = SpatialHashGrid(cell_size=2.0 * 10)
        self.solver_iterations = 20

        self.containers: list[Container] = []
        self.constraints: list[Constraint] = []

    def add_particle(self, particle: Particle) -> None:
        self.particles.append(particle)

    def clear(self) -> None:
        """Removes all particles and constraints."""
        self.particles.clear()
        self.constraints.clear()

    def remove_dead(self) -> None:
        """Removes particles marked as dead."""
        self.particles = [p for p in self.particles if p.alive]

    def add_global_force(self, force: Force) -> None:
        self.global_forces.append(force)

    def add_local_force(self, force: Force) -> None:
        self.local_forces.append(force)

    def clear_forces(self) -> None:
        self.global_forces.clear()
        self.local_forces.clear()

    def add_container(self, container: Container) -> None:
        self.containers.append(container)

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the system."""
        self.constraints.append(constraint)

    def step(self, dt: float) -> None:
        """
        Advances the particle simulation by dt.
        """
        if self.paused:
            return

        # apply forces on the particles
        for p in self.particles:
            if not p.alive or p.sleeping:  # early out
                continue
            for force in self.global_forces:
                force.apply(p, dt)
            for force in self.local_forces:
                force.apply(p, dt)

        # integrating the particles using verlet integration
        for p in self.particles:
            integrate_particle(p, dt)

        # broadphase collision detection
        self.broadphase.clear()
        for p in self.particles:
            if p.alive:
                self.broadphase.insert(p)
        candidate_pairs = self.broadphase.compute_pairs()

        # narrowphase collision detection
        contacts = []
        for a, b in candidate_pairs:
            contact = circle_circle(a, b)
            if contact is not None:
                contacts.append(contact)

        for p in self.particles:
            if not p.alive:
                continue
            for container in self.containers:
                contacts.extend(container.generate_contacts(p))

        # solving collisions and constraints iteratively to account for
        # multiple overlaps
        for _ in range(self.solver_iterations):
            # solving collision
            for contact in contacts:
                resolve_contact(contact)

            # solving constraints
            for constraint in self.constraints:
                constraint.solve(dt)

        # applying positional correction to decouple overlapping objects
        for contact in contacts:
            positional_correction(contact)

        # removing dead particles
        self.remove_dead()
