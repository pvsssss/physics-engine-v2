from __future__ import annotations
from typing import List

from engine.physics.particle import Particle
from engine.physics.forces import Force
from engine.physics.integrate import integrate_particle
from engine.physics.collision.broadphase import SpatialHashGrid
from engine.physics.collision.circle_circle import circle_circle
from engine.physics.solver import resolve_contact, positional_correction
from engine.physics.containers.base import Container
from engine.physics.constraints.base import Constraint


class ParticleSystem:
    """
    Owns and updates all live particles.

    Responsibilities:
    - apply forces
    - advance simulation via integrator
    - remove dead particles
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
        self.solver_iterations = 16
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

        # 1. Apply forces
        for p in self.particles:
            if not p.alive or p.sleeping:
                continue
            for force in self.global_forces:
                force.apply(p, dt)
            for force in self.local_forces:
                force.apply(p, dt)

        # 2. Integrate particles FIRST (before constraints)
        for p in self.particles:
            integrate_particle(p, dt)

        # 3. Broadphase (spatial hash)
        self.broadphase.clear()
        for p in self.particles:
            if p.alive:
                self.broadphase.insert(p)
        candidate_pairs = self.broadphase.compute_pairs()

        # 4. Narrowphase (generate contacts)
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

        # 5. Solve collisions AND constraints iteratively
        for _ in range(self.solver_iterations):
            # Solve collisions
            for contact in contacts:
                resolve_contact(contact)

            # Solve constraints (with dt for velocity correction)
            for constraint in self.constraints:
                constraint.solve(dt)

        # 6. Apply positional correction ONCE at the end
        for contact in contacts:
            positional_correction(contact)

        # 7. Cleanup
        self.remove_dead()
