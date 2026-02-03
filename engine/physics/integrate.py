from __future__ import annotations

from engine.physics.particle import Particle


def integrate_particle(p: Particle, dt: float) -> None:
    """
    Advances a single particle by one timestep using
    Velocity Verlet integration.

    Velocity Verlet algorithm:
    1. x_new = x + v*dt + 0.5*a*dt^2
    (position from current velocity and acceleration)
    2. a_new = F/m
    (compute new acceleration at new position)
    3. v_new = v + 0.5*(a + a_new)*dt
    (velocity from average of old and new acceleration)

    We are using Verlet here instead of euler as it gives better energy
    conservation than any of the euler methods

    using dt as a parameter for if we ever want to change it in the
    future
    """

    # early out statements
    if not p.alive:
        return

    if p.sleeping:
        return

    if p.inv_mass == 0.0:  # static particles
        p.force.x = 0.0
        p.force.y = 0.0
        return

    # storing current acceleration from last frame to use in verlet
    accel_old_x = p.acceleration.x
    accel_old_y = p.acceleration.y

    # step 1: update position using current velocity and acceleration
    # x_new = x + v*dt + 0.5*a*dt^2
    dt_sq = dt * dt
    p.position.x += p.velocity.x * dt + 0.5 * accel_old_x * dt_sq
    p.position.y += p.velocity.y * dt + 0.5 * accel_old_y * dt_sq

    # step 2: calculate new acceleration at new position using forces
    # accumulated on the body
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

    # Apply damping to reduce the velocity of the body gradually over
    # time
    if p.damping > 0.0:
        # Exponential decay: v *= (1 - damping)^dt
        # we are calculating damping using timestep for a much more
        # deterministic behaviour
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
            return
    else:
        # if particle has enough speed then reset the sleep timer
        p.sleep_timer = 0.0

    # Clear forces for next frame
    p.force.x = 0.0
    p.force.y = 0.0
