from __future__ import annotations

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity, WindForce
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.particle_system import ParticleSystem

from engine.scenes import projectile_config as config_static
from engine.core.config_manager import config_manager


def build(system: ParticleSystem) -> None:
    system.clear()
    system.clear_forces()
    system.containers.clear()

    # 1. Get the dynamic config memory instead of static defaults
    cfg = config_manager.get_scene_config("projectile_scene")

    container = RectangleContainer(
        config_static.CONTAINER_X,
        config_static.CONTAINER_Y,
        config_static.CONTAINER_WIDTH,
        config_static.CONTAINER_HEIGHT,
    )
    system.add_container(container)

    # 2. Apply forces using deep copies from the memory bank to prevent mutation
    system.add_global_force(Gravity(cfg["gravity"].copy()))

    if not cfg["wind_force"].is_zero():
        system.add_global_force(WindForce(cfg["wind_force"].copy()))

    # 3. Spawn particle using the dynamic memory
    projectile = Particle(
        position=config_static.INITIAL_POSITION.copy(),
        velocity=cfg["initial_velocity"].copy(),
        radius=cfg["particle_radius"],
        mass=cfg["particle_mass"],
        restitution=cfg["restitution"] if config_static.ENABLE_BOUNCE else 0.0,
        friction=cfg["friction"],
        damping=cfg["damping"],
        sleep_threshold=5.0,
    )
    system.add_particle(projectile)
