from __future__ import annotations

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.forces import Gravity, WindForce
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.particle_system import ParticleSystem
from engine.scenes import projectile_config as config


# Screen height for coordinate transformation
# This should match your render_config.py SCREEN_HEIGHT
SCREEN_HEIGHT = 700.0


def bottom_left_to_top_left(position: Vec2) -> Vec2:
    """
    Converts position from bottom-left origin (physics convention)
    to top-left origin (graphics convention).

    Bottom-left: (0, 0) at bottom-left, Y increases upward
    Top-left: (0, 0) at top-left, Y increases downward
    """
    return Vec2(position.x, SCREEN_HEIGHT - position.y)


def build(system: ParticleSystem) -> None:
    """
    Builds a projectile motion scene with configurable initial conditions.
    Uses bottom-left origin coordinate system in config for intuitive physics.
    """
    system.clear()
    system.clear_forces()
    system.containers.clear()

    # Transform container bounds from bottom-left to top-left origin
    # Bottom-left container: (x, y) is bottom-left corner, extends right and up
    # Top-left container: needs (x, y) at top-left corner, extends right and down
    container_bottom_left = Vec2(config.CONTAINER_X, config.CONTAINER_Y)
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

    # Transform gravity from bottom-left to top-left coordinate system
    # In bottom-left coords: negative Y is downward
    # In top-left coords: positive Y is downward
    # So we negate the Y component
    gravity_engine = Vec2(config.GRAVITY.x, -config.GRAVITY.y)
    gravity = Gravity(gravity_engine)
    system.add_global_force(gravity)

    # Wind force X component stays the same (horizontal)
    # Wind force Y component needs to be negated (vertical direction flipped)
    if not config.WIND_FORCE.is_zero():
        wind_engine = Vec2(config.WIND_FORCE.x, -config.WIND_FORCE.y)
        wind = WindForce(wind_engine)
        system.add_global_force(wind)

    # Transform initial position and velocity
    initial_position_engine = bottom_left_to_top_left(config.INITIAL_POSITION)

    # Velocity: X stays same, Y gets negated (up in physics = negative in graphics)
    initial_velocity_engine = Vec2(
        config.INITIAL_VELOCITY.x, -config.INITIAL_VELOCITY.y
    )

    # Create projectile particle
    projectile = Particle(
        position=initial_position_engine,
        velocity=initial_velocity_engine,
        radius=config.PARTICLE_RADIUS,
        mass=config.PARTICLE_MASS,
        restitution=config.RESTITUTION if config.ENABLE_BOUNCE else 0.0,
        friction=config.FRICTION,
        damping=config.DAMPING,
        sleep_threshold=0.0,  # Disable sleeping for projectile
    )
    system.add_particle(projectile)
