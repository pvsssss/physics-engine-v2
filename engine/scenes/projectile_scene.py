from __future__ import annotations

from engine.physics.particle import Particle
from engine.physics.forces import Gravity, WindForce
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.particle_system import ParticleSystem
from engine.scenes import projectile_config as config


def build(system: ParticleSystem) -> None:
    system.clear()
    system.clear_forces()
    system.containers.clear()

    container = RectangleContainer(
        config.CONTAINER_X,
        config.CONTAINER_Y,
        config.CONTAINER_WIDTH,
        config.CONTAINER_HEIGHT,
    )
    system.add_container(container)

    system.add_global_force(Gravity(config.GRAVITY))

    if not config.WIND_FORCE.is_zero():
        system.add_global_force(WindForce(config.WIND_FORCE))

    projectile = Particle(
        position=config.INITIAL_POSITION.copy(),
        velocity=config.INITIAL_VELOCITY.copy(),
        radius=config.PARTICLE_RADIUS,
        mass=config.PARTICLE_MASS,
        restitution=config.RESTITUTION if config.ENABLE_BOUNCE else 0.0,
        friction=config.FRICTION,
        damping=config.DAMPING,
        sleep_threshold=0.0,
    )
    system.add_particle(projectile)
