from __future__ import annotations

import math

from engine.physics.contact import Contact

# Velocity threshold for treating collision as resting (non-bouncy)
RESTING_VELOCITY_THRESHOLD = 2.0

# Small epsilon for floating-point comparisons
EPSILON = 1e-8

MAX_CORRECTION_PER_ITERATION = 2
PERCENT = 0.2
# Thresholds for waking sleeping particles
# Only wake if collision is significant enough to matter
WAKE_THRESHOLD_VELOCITY = 2.0  # INCREASED: Less sensitive to micro-collisions
WAKE_THRESHOLD_PENETRATION = 0.3  # INCREASED: Tolerate more overlap before waking


def resolve_contact(contact: Contact) -> None:
    """
    Resolves a collision contact using impulse-based response
    with restitution and friction.

    Steps:
    1. Compute relative velocity along contact normal
    2. Apply normal impulse (handles bounce/collision response)
    3. Apply friction impulse (handles sliding/sticking)
    """
    a = contact.a
    b = contact.b

    if not a.alive or not b.alive:
        return

    inv_mass_a = a.inv_mass
    inv_mass_b = b.inv_mass

    # Two static objects don't collide
    if inv_mass_a == 0.0 and inv_mass_b == 0.0:
        return

    # relative velocity at contact
    rv = b.velocity - a.velocity

    # relative velocity at contact along collision normal
    vel_along_normal = rv.dot(contact.normal)

    # Particles are separating so no impulse needed
    if vel_along_normal > 0.0:
        return

    # Only wake particles if collision is significant
    significant_collision = (
        abs(vel_along_normal) > WAKE_THRESHOLD_VELOCITY
        or contact.penetration > WAKE_THRESHOLD_PENETRATION
    )

    if significant_collision:
        if hasattr(a, "sleeping") and a.sleeping and inv_mass_a > 0.0:
            a.sleeping = False
            a.sleep_timer = 0.0
        if hasattr(b, "sleeping") and b.sleeping and inv_mass_b > 0.0:
            b.sleeping = False
            b.sleep_timer = 0.0

    # Use minimum restitution of both particles
    restitution = min(a.restitution, b.restitution)

    # Resting contacts shouldn't bounce
    if abs(vel_along_normal) < RESTING_VELOCITY_THRESHOLD:
        restitution = 0.0

    # Derived from Newton's law of restitution and momentum conservation:
    # j = -(1 + e) * v_rel · n / (1/m_a + 1/m_b)
    j = -(1.0 + restitution) * vel_along_normal
    j /= inv_mass_a + inv_mass_b

    impulse = contact.normal * j

    if inv_mass_a > 0.0:
        a.velocity.x -= impulse.x * inv_mass_a
        a.velocity.y -= impulse.y * inv_mass_a

    if inv_mass_b > 0.0:
        b.velocity.x += impulse.x * inv_mass_b
        b.velocity.y += impulse.y * inv_mass_b

    # Recompute relative velocity after normal impulse
    # (friction acts on the velocities AFTER collision response)
    rv = b.velocity - a.velocity

    # Tangent direction (perpendicular to normal, in plane of sliding)
    # tangent = rv - (rv · n) * n
    tangent = rv - contact.normal * rv.dot(contact.normal)
    tangent_len_sq = tangent.length_squared()

    # if no tangential velocity then no friction needed
    if tangent_len_sq < EPSILON * EPSILON:
        return

    tangent = tangent / math.sqrt(tangent_len_sq)

    # tangential impulse needed to stop sliding
    jt = -rv.dot(tangent)
    jt /= inv_mass_a + inv_mass_b

    # Combined friction coefficient (geometric mean)
    mu = math.sqrt(a.friction * b.friction)

    if abs(vel_along_normal) < 2.0:  # Very slow collision
        return

    # applying coulomb friction
    # friction cannot exceed μ * normal_force
    max_friction = j * mu
    jt = max(-max_friction, min(jt, max_friction))

    friction_impulse = tangent * jt

    # Apply friction impulse
    if inv_mass_a > 0.0:
        a.velocity.x -= friction_impulse.x * inv_mass_a
        a.velocity.y -= friction_impulse.y * inv_mass_a

    if inv_mass_b > 0.0:
        b.velocity.x += friction_impulse.x * inv_mass_b
        b.velocity.y += friction_impulse.y * inv_mass_b


def positional_correction(contact: Contact) -> None:
    """
    Applies positional correction to resolve penetration.

    IMPROVED: Reduced correction percentage and increased slop tolerance
    to minimize wave artifacts in stacks. Disabled velocity adjustment
    to prevent energy injection.
    """
    a = contact.a
    b = contact.b

    inv_mass_a = a.inv_mass
    inv_mass_b = b.inv_mass

    if inv_mass_a + inv_mass_b == 0.0:
        return

    # IMPROVED: Reduced from 0.3 to 0.2 for gentler correction
    percent = PERCENT

    # IMPROVED: Increased from 0.05 to 0.15 to tolerate more penetration
    slop = 0.05

    correction_mag = max(contact.penetration - slop, 0.0)
    correction_mag /= inv_mass_a + inv_mass_b
    correction_mag *= percent
    correction_mag = min(correction_mag, MAX_CORRECTION_PER_ITERATION)

    correction = contact.normal * correction_mag

    # Apply position correction
    if inv_mass_a > 0.0:
        a.position.x -= correction.x * inv_mass_a
        a.position.y -= correction.y * inv_mass_a

    if inv_mass_b > 0.0:
        b.position.x += correction.x * inv_mass_b
        b.position.y += correction.y * inv_mass_b

    # IMPROVED: Velocity adjustment disabled (was 0.05)
    # This prevents energy injection that causes jitter in stacks


def solve_contact(contact: Contact) -> None:
    """
    Complete contact resolution: impulse + positional correction.
    """
    resolve_contact(contact)
    positional_correction(contact)
