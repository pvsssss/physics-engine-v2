from __future__ import annotations
from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.particle_system import ParticleSystem
from engine.physics.constraints.distance_constraint import DistanceConstraint
from engine.core.config_manager import config_manager


def build(system: ParticleSystem) -> None:
    system.clear()
    system.clear_forces()
    system.containers.clear()

    cfg = config_manager.get_scene_config("rope_scene")

    system.add_container(RectangleContainer(0.0, 0.0, 1236.0, 864.0))
    system.add_global_force(Gravity(cfg["gravity"]))

    rope_length = cfg["particle_count"]  # Dynamically load count!
    particles = []

    for i in range(rope_length):
        mass = float("inf") if i == 0 else 10.0
        velocity_scale = i / rope_length
        p = Particle(
            position=Vec2(620.0, 664.0 - i * 30.0),
            velocity=Vec2(500.0 * velocity_scale, -100.0),
            radius=8.0,
            mass=mass,
            restitution=0.2,
            friction=0.5,
        )
        particles.append(p)
        system.add_particle(p)

    for i in range(len(particles) - 1):
        system.add_constraint(
            DistanceConstraint(
                particles[i], particles[i + 1], distance=30.0, stiffness=0.5
            )
        )
