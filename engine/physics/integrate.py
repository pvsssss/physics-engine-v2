from __future__ import annotations

from engine.math.vec import Vec2
from engine.physics.particle import Particle


def integrate_particle(p: Particle, dt: float) -> None:
    """
    Advances a single particle by one timestep using
    Velocity Verlet integration.

    Velocity Verlet algorithm:
    1. x_new = x + v*dt + 0.5*a*dt^2     (position from current velocity and acceleration)
    2. a_new = F/m                        (compute new acceleration at new position)
    3. v_new = v + 0.5*(a + a_new)*dt    (velocity from average of old and new acceleration)

    This gives excellent energy conservation and is more stable than Euler methods.

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

    # Store current acceleration from last frame
    accel_old_x = p.acceleration.x
    accel_old_y = p.acceleration.y

    # Step 1: Update position using current velocity and acceleration
    # x_new = x + v*dt + 0.5*a*dt^2
    dt_sq = dt * dt
    p.position.x += p.velocity.x * dt + 0.5 * accel_old_x * dt_sq
    p.position.y += p.velocity.y * dt + 0.5 * accel_old_y * dt_sq

    # Step 2: Calculate NEW acceleration at new position
    accel_new_x = p.force.x * p.inv_mass
    accel_new_y = p.force.y * p.inv_mass

    # Store new acceleration for next frame
    p.acceleration.x = accel_new_x
    p.acceleration.y = accel_new_y

    # Step 3: Update velocity using AVERAGE of old and new acceleration
    # v_new = v + 0.5*(a_old + a_new)*dt
    avg_accel_x = 0.5 * (accel_old_x + accel_new_x)
    avg_accel_y = 0.5 * (accel_old_y + accel_new_y)

    p.velocity.x += avg_accel_x * dt
    p.velocity.y += avg_accel_y * dt

    # Apply damping
    if p.damping > 0.0:
        # Exponential decay: v *= (1 - damping)^dt
        # This ensures consistent behavior regardless of timestep
        clamped_damping = min(p.damping, 0.999)  # Never >= 1.0
        damping_factor = pow(1.0 - clamped_damping, dt)
        p.velocity.x *= damping_factor
        p.velocity.y *= damping_factor

    # Sleep detection
    speed_sq = p.velocity.length_squared()
    threshold_sq = p.sleep_threshold * p.sleep_threshold

    if speed_sq < threshold_sq:
        p.sleep_timer += dt
        if p.sleep_timer >= 0.3:
            # Put particle to sleep
            p.sleeping = True
            p.velocity.x = 0.0
            p.velocity.y = 0.0
            p.force.x = 0.0
            p.force.y = 0.0
            p.acceleration.x = 0.0
            p.acceleration.y = 0.0
            return  # Don't clear forces below
    else:
        # Particle moving fast enough - reset sleep timer
        p.sleep_timer = 0.0

    # Clear forces for next frame
    p.force.x = 0.0
    p.force.y = 0.0
