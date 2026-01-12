from __future__ import annotations

from engine.math.vec import Vec2
from engine.physics.particle import Particle


def integrate_particle(p: Particle, dt: float) -> None:
    """
    Advances a single particle by one timestep using
    semi-implicit Euler integration.

    Semi-implicit Euler:
    1. v_new = v_old + a * dt  (explicit velocity update)
    2. x_new = x_old + v_new * dt  (implicit position update using new velocity)

    This gives much better energy conservation than explicit Euler.

    Assumes:
     forces have already been accumulated
     collisions are handled elsewhere
    """

    if not p.alive:
        return

    if p.sleeping:
        return

    if p.inv_mass == 0.0:
        # Static particle - clear forces and skip integration
        p.force.x = 0.0
        p.force.y = 0.0
        return

    # acceleration from accumulated forces
    # a = F / m = F * inv_mass
    accel = p.force * p.inv_mass

    # velocity integration (semi-implicit Euler
    # v_new = v_old + a * dt
    p.velocity.x += accel.x * dt
    p.velocity.y += accel.y * dt

    if p.damping > 0.0:
        # Exponential decay: v *= (1 - damping)^dt
        # This ensures consistent behavior regardless of timestep
        clamped_damping = min(p.damping, 0.999)  # Never >= 1.0
        damping_factor = pow(1.0 - clamped_damping, dt)
        p.velocity.x *= damping_factor
        p.velocity.y *= damping_factor

    speed_sq = p.velocity.length_squared()
    threshold_sq = p.sleep_threshold * p.sleep_threshold

    if speed_sq < threshold_sq:
        p.sleep_timer += dt
        if p.sleep_timer >= 0.5:
            # Put particle to sleep
            p.sleeping = True
            p.velocity.x = 0.0
            p.velocity.y = 0.0
            p.force.x = 0.0
            p.force.y = 0.0
            return  # Don't update position this frame
    else:
        # Particle moving fast enough - reset sleep timer
        p.sleep_timer = 0.0

    # x_new = x_old + v_new * dt  (using UPDATED velocity)
    p.position.x += p.velocity.x * dt
    p.position.y += p.velocity.y * dt

    # Clear forces for next frame
    p.force.x = 0.0
    p.force.y = 0.0
