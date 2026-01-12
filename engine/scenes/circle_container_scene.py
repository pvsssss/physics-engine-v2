from __future__ import annotations
import random

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.containers.circle_container import CircleContainer
from engine.physics.particle_system import ParticleSystem


def build(system: ParticleSystem) -> None:
    """
    Test scene:
    - gravity
    - rectangular container (1000 x 700)
    - 10 particles
    """

    system.clear()
    system.clear_forces()
    system.containers.clear()

    container = CircleContainer(Vec2(500.0, 350.0), 300.0)
    system.add_container(container)

    gravity = Gravity(Vec2(0.0, 1200.0))
    system.add_global_force(gravity)

    for i in range(10):
        p = Particle(
            position=Vec2(
                random.uniform(250.0, 750.0),
                350.0,
            ),
            velocity=Vec2(random.uniform(-100.0, 100.0), random.uniform(-100.0, 100.0)),
            radius=10.0,
            mass=1.0,
            restitution=0.6,
            friction=0.3,
            sleep_threshold=4.5,
        )
        system.add_particle(p)
