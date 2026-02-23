from __future__ import annotations
import random
import math

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity, BuoyancyForce, WaterDragForce, LinearDrag
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.particle_system import ParticleSystem

from engine.scenes import buoyancy_config as config_static
from engine.core.config_manager import config_manager


def interpolate_color(color1: tuple, color2: tuple, t: float) -> tuple:
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return (r, g, b)


def density_to_color(density: float, cfg: dict) -> tuple:
    density_range = cfg["density_max"] - cfg["density_min"]
    if density_range == 0:
        normalized = 0.5
    else:
        normalized = (density - cfg["density_min"]) / density_range
    normalized = max(0.0, min(1.0, normalized))

    if normalized < 0.5:
        t = normalized * 2.0
        return interpolate_color(
            config_static.COLOR_LOW_DENSITY, config_static.COLOR_MID_DENSITY, t
        )
    else:
        t = (normalized - 0.5) * 2.0
        return interpolate_color(
            config_static.COLOR_MID_DENSITY, config_static.COLOR_HIGH_DENSITY, t
        )


def build(system: ParticleSystem) -> None:
    system.clear()
    system.clear_forces()
    system.containers.clear()

    cfg = config_manager.get_scene_config("buoyancy_scene")

    if config_static.SOLVER_ITERATIONS is not None:
        system.solver_iterations = config_static.SOLVER_ITERATIONS

    system.add_container(
        RectangleContainer(
            config_static.CONTAINER_X,
            config_static.CONTAINER_Y,
            config_static.CONTAINER_WIDTH,
            config_static.CONTAINER_HEIGHT,
        )
    )

    system.add_global_force(Gravity(cfg["gravity"]))
    system.add_global_force(LinearDrag(cfg["air_drag"]))

    system.add_global_force(
        BuoyancyForce(
            water_top=config_static.WATER_Y_TOP,
            water_bottom=config_static.WATER_Y_BOTTOM,
            fluid_density=cfg["fluid_density"],
            gravity_magnitude=abs(cfg["gravity"].y),
        )
    )

    system.add_global_force(
        WaterDragForce(
            water_top=config_static.WATER_Y_TOP,
            water_bottom=config_static.WATER_Y_BOTTOM,
            fluid_density=cfg["fluid_density"],
            drag_coefficient=cfg["water_drag"],
        )
    )

    # Use dynamic particle count!
    for _ in range(cfg["particle_count"]):
        radius = random.uniform(cfg["radius_min"], cfg["radius_max"])
        density = random.uniform(cfg["density_min"], cfg["density_max"])
        mass = density * (math.pi * radius * radius)

        spawn_pos = Vec2(
            random.uniform(config_static.SPAWN_X_MIN, config_static.SPAWN_X_MAX),
            random.uniform(config_static.SPAWN_Y_MIN, config_static.SPAWN_Y_MAX),
        )

        velocity = Vec2(
            random.uniform(
                config_static.SPAWN_VELOCITY_X_MIN, config_static.SPAWN_VELOCITY_X_MAX
            ),
            random.uniform(
                config_static.SPAWN_VELOCITY_Y_MIN, config_static.SPAWN_VELOCITY_Y_MAX
            ),
        )

        particle = Particle(
            position=spawn_pos,
            velocity=velocity,
            radius=radius,
            mass=mass,
            restitution=config_static.PARTICLE_RESTITUTION,
            friction=config_static.PARTICLE_FRICTION,
            damping=config_static.PARTICLE_DAMPING,
            sleep_threshold=config_static.SLEEP_THRESHOLD,
        )
        particle.density = density
        particle.color = density_to_color(density, cfg)
        system.add_particle(particle)
