from __future__ import annotations
import random

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity
from engine.physics.containers.circle_container import CircleContainer
from engine.physics.particle_system import ParticleSystem
from engine.core.config_manager import config_manager


def build(system: ParticleSystem) -> None:
    system.clear()
    system.clear_forces()
    system.containers.clear()

    cfg = config_manager.get_scene_config("circle_container_scene")

    system.add_container(CircleContainer(Vec2(618.0, 432.0), 400.0))
    system.add_global_force(Gravity(cfg["gravity"]))

    # Use dynamic particle count!
    for i in range(cfg["particle_count"]):
        p = Particle(
            position=Vec2(random.uniform(250.0, 750.0), 514.0),
            velocity=Vec2(random.uniform(-100.0, 100.0), random.uniform(-100.0, 100.0)),
            radius=cfg.get("radius", 10.0),
            mass=cfg.get("mass", 1.0),
            restitution=cfg.get("restitution", 0.7),
            friction=cfg.get("friction", 0.1),
            damping=cfg.get("damping", 0.05),
            sleep_threshold=5.0,
        )
        system.add_particle(p)
