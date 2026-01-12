from __future__ import annotations
from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.particle_system import ParticleSystem
from engine.physics.constraints.distance_constraint import DistanceConstraint


def build(system: ParticleSystem) -> None:
    """
    Rope demo: Chain of particles connected by distance constraints
    """
    system.clear()
    system.clear_forces()
    system.containers.clear()

    # Container
    container = RectangleContainer(0.0, 0.0, 1000.0, 700.0)
    system.add_container(container)

    # Gravity
    gravity = Gravity(Vec2(0.0, 800.0))
    system.add_global_force(gravity)

    # Create rope chain
    rope_length = 8
    particles = []

    for i in range(rope_length):
        # First particle is static (pinned to ceiling)
        mass = float("inf") if i == 0 else 1.0

        p = Particle(
            position=Vec2(500.0, 100.0 + i * 30.0),
            velocity=Vec2(0.0, 0.0),
            radius=8.0,
            mass=mass,
            restitution=0.2,
            friction=0.5,
        )
        particles.append(p)
        system.add_particle(p)

    # Connect particles with distance constraints
    for i in range(len(particles) - 1):
        constraint = DistanceConstraint(
            particles[i],
            particles[i + 1],
            distance=30.0,  # Fixed distance
            stiffness=1.0,  # Rigid rope (use 0.5 for stretchy)
        )
        system.add_constraint(constraint)
