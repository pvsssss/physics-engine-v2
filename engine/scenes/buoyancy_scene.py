from __future__ import annotations
import random
import math

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity, BuoyancyForce, WaterDragForce, LinearDrag
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.particle_system import ParticleSystem
from engine.scenes import buoyancy_config as config


# Screen height for coordinate transformation
SCREEN_HEIGHT = 700.0


def bottom_left_to_top_left(position: Vec2) -> Vec2:
    """
    Converts position from bottom-left origin (physics convention)
    to top-left origin (graphics convention).
    """
    return Vec2(position.x, SCREEN_HEIGHT - position.y)


def interpolate_color(color1: tuple, color2: tuple, t: float) -> tuple:
    """
    Linearly interpolate between two RGB colors.
    t=0.0 returns color1, t=1.0 returns color2
    """
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return (r, g, b)


def density_to_color(density: float) -> tuple:
    """
    Maps particle density to color using a gradient:
    Low density (floats) → Red
    Mid density → Purple
    High density (sinks) → Blue
    """
    # Normalize density to [0, 1] range
    density_range = config.PARTICLE_DENSITY_MAX - config.PARTICLE_DENSITY_MIN
    normalized = (density - config.PARTICLE_DENSITY_MIN) / density_range
    normalized = max(0.0, min(1.0, normalized))  # Clamp to [0, 1]

    # Two-part gradient: red → purple → blue
    if normalized < 0.5:
        # First half: red to purple
        t = normalized * 2.0  # Scale to [0, 1]
        return interpolate_color(config.COLOR_LOW_DENSITY, config.COLOR_MID_DENSITY, t)
    else:
        # Second half: purple to blue
        t = (normalized - 0.5) * 2.0  # Scale to [0, 1]
        return interpolate_color(config.COLOR_MID_DENSITY, config.COLOR_HIGH_DENSITY, t)


def build(system: ParticleSystem) -> None:
    """
    Builds a buoyancy simulation scene with particles of varying densities.
    """
    system.clear()
    system.clear_forces()
    system.containers.clear()

    # Set solver iterations for better collision resolution with heavy particles
    system.solver_iterations = config.SOLVER_ITERATIONS

    # Create container (full screen bounds)
    container_top_left = bottom_left_to_top_left(
        Vec2(config.CONTAINER_X, config.CONTAINER_Y + config.CONTAINER_HEIGHT)
    )
    container = RectangleContainer(
        container_top_left.x,
        container_top_left.y,
        config.CONTAINER_WIDTH,
        config.CONTAINER_HEIGHT,
    )
    system.add_container(container)

    # Add gravity (flip Y for top-left coords)
    gravity_engine = Vec2(config.GRAVITY.x, -config.GRAVITY.y)
    gravity = Gravity(gravity_engine)
    system.add_global_force(gravity)

    # Add air drag (global, helps dampen bobbing at surface)
    air_drag = LinearDrag(config.AIR_DRAG_COEFFICIENT)
    system.add_global_force(air_drag)

    # Convert water bounds to engine coordinates (top-left origin)
    water_top_engine = SCREEN_HEIGHT - config.WATER_Y_TOP
    water_bottom_engine = SCREEN_HEIGHT - config.WATER_Y_BOTTOM

    # Add buoyancy force (regional, only in water)
    buoyancy = BuoyancyForce(
        water_top=water_top_engine,
        water_bottom=water_bottom_engine,
        fluid_density=config.FLUID_DENSITY,
        gravity_magnitude=abs(config.GRAVITY.y),
    )
    system.add_global_force(buoyancy)

    # Add water drag force (regional, only in water)
    water_drag = WaterDragForce(
        water_top=water_top_engine,
        water_bottom=water_bottom_engine,
        fluid_density=config.FLUID_DENSITY,
        drag_coefficient=config.WATER_DRAG_COEFFICIENT,
    )
    system.add_global_force(water_drag)

    # Spawn particles with varying densities
    for _ in range(config.PARTICLE_COUNT):
        # Random radius
        radius = random.uniform(config.PARTICLE_RADIUS_MIN, config.PARTICLE_RADIUS_MAX)

        # Random density
        density = random.uniform(
            config.PARTICLE_DENSITY_MIN, config.PARTICLE_DENSITY_MAX
        )

        # Calculate mass from density and area
        # In 2D: mass = density * area
        # For circle: area = π * r²
        area = math.pi * radius * radius
        mass = density * area

        # Random spawn position (bottom-left coords)
        spawn_pos = Vec2(
            random.uniform(config.SPAWN_X_MIN, config.SPAWN_X_MAX),
            random.uniform(config.SPAWN_Y_MIN, config.SPAWN_Y_MAX),
        )

        # Convert to engine coords
        spawn_pos_engine = bottom_left_to_top_left(spawn_pos)

        # Random velocity (flip Y for engine coords)
        velocity = Vec2(
            random.uniform(config.SPAWN_VELOCITY_X_MIN, config.SPAWN_VELOCITY_X_MAX),
            -random.uniform(config.SPAWN_VELOCITY_Y_MIN, config.SPAWN_VELOCITY_Y_MAX),
        )

        # Calculate color based on density
        color = density_to_color(density)

        # Create particle
        particle = Particle(
            position=spawn_pos_engine,
            velocity=velocity,
            radius=radius,
            mass=mass,
            restitution=config.PARTICLE_RESTITUTION,
            friction=config.PARTICLE_FRICTION,
            damping=config.PARTICLE_DAMPING,
            sleep_threshold=config.SLEEP_THRESHOLD,
        )

        # Store density and color as custom attributes
        # (We'll use these for rendering)
        particle.density = density
        particle.color = color

        system.add_particle(particle)
    # floating_particle = Particle(
    #     position=Vec2(100.0, 100.0),
    #     velocity=Vec2(0.0, 0.0),
    #     radius=10.0,
    #     mass=3.1416,
    #     restitution=config.PARTICLE_RESTITUTION,
    #     friction=config.PARTICLE_FRICTION,
    #     damping=config.PARTICLE_DAMPING,
    #     sleep_threshold=config.SLEEP_THRESHOLD,
    # )
    # floating_particle.density = 100.0
    # floating_particle.color = (150, 50, 200)
    # system.add_particle(floating_particle)
