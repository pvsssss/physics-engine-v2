from __future__ import annotations
import math

from engine.physics.contact import Contact


# Velocity threshold for treating collision as resting (non-bouncy)
RESTING_VELOCITY_THRESHOLD = 1.0

# Small epsilon for floating-point comparisons
EPSILON = 1e-8

# Thresholds for waking sleeping particles
# Only wake if collision is significant enough to matter
WAKE_THRESHOLD_VELOCITY = 0.1  # Wake if relative velocity > this
WAKE_THRESHOLD_PENETRATION = 0.1  # Wake if penetration > this


def resolve_contact(contact: Contact) -> None:
    """
    Resolves a collision contact using impulse-based response
    with restitution and friction.

    Steps:
    1. Compute relative velocity along contact normal
    2. Apply normal impulse (handles bounce/collision response)
    3. Apply friction impulse (handles sliding/sticking)

    Smart wake logic:
    - Only wakes sleeping particles if collision is significant
    - Prevents jitter from micro-corrections on resting particles
    """

    a = contact.a
    b = contact.b

    # -------------------------------------------------
    # Early exits
    # -------------------------------------------------
    if hasattr(a, "position"):
        print(
            f"Solving: a.pos={a.position.y:.1f}, a.sleeping={getattr(a, 'sleeping', 'N/A')}, penetration={contact.penetration:.2f}"
        )

    if not a.alive or not b.alive:
        return

    inv_mass_a = a.inv_mass
    inv_mass_b = b.inv_mass

    # Two static objects don't collide
    if inv_mass_a == 0.0 and inv_mass_b == 0.0:
        return

    # -------------------------------------------------
    # Relative velocity at contact
    # -------------------------------------------------

    rv = b.velocity - a.velocity
    vel_along_normal = rv.dot(contact.normal)

    # Particles are separating - no impulse needed
    if vel_along_normal > 0.0:
        return

    # -------------------------------------------------
    # Smart wake logic (before applying impulse)
    # -------------------------------------------------

    # Only wake particles if collision is significant
    # This prevents sleep/wake jitter from tiny corrections
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

    # -------------------------------------------------
    # Restitution (bounciness)
    # -------------------------------------------------

    # Use minimum restitution (most conservative)
    restitution = min(a.restitution, b.restitution)

    # Resting contacts shouldn't bounce
    if abs(vel_along_normal) < RESTING_VELOCITY_THRESHOLD:
        restitution = 0.0

    # -------------------------------------------------
    # Normal impulse magnitude
    # -------------------------------------------------

    # Derived from Newton's law of restitution and momentum conservation:
    # j = -(1 + e) * v_rel · n / (1/m_a + 1/m_b)
    j = -(1.0 + restitution) * vel_along_normal
    j /= inv_mass_a + inv_mass_b

    impulse = contact.normal * j

    # -------------------------------------------------
    # Apply normal impulse
    # -------------------------------------------------

    if inv_mass_a > 0.0:
        a.velocity.x -= impulse.x * inv_mass_a
        a.velocity.y -= impulse.y * inv_mass_a

    if inv_mass_b > 0.0:
        b.velocity.x += impulse.x * inv_mass_b
        b.velocity.y += impulse.y * inv_mass_b

    # -------------------------------------------------
    # Friction impulse (tangential to contact)
    # -------------------------------------------------

    # Recompute relative velocity after normal impulse
    # (friction acts on the velocities AFTER collision response)
    rv = b.velocity - a.velocity

    # Tangent direction (perpendicular to normal, in plane of sliding)
    # tangent = rv - (rv · n) * n
    tangent = rv - contact.normal * rv.dot(contact.normal)

    tangent_len_sq = tangent.length_squared()

    # No tangential velocity - no friction needed
    if tangent_len_sq < EPSILON * EPSILON:
        return

    tangent = tangent / math.sqrt(tangent_len_sq)

    # -------------------------------------------------
    # Friction impulse magnitude
    # -------------------------------------------------

    # Tangential impulse needed to stop sliding
    jt = -rv.dot(tangent)
    jt /= inv_mass_a + inv_mass_b

    # Combined friction coefficient (geometric mean)
    mu = math.sqrt(a.friction * b.friction)

    # Coulomb friction: friction cannot exceed μ * normal_force
    max_friction = j * mu
    jt = max(-max_friction, min(jt, max_friction))

    friction_impulse = tangent * jt

    # -------------------------------------------------
    # Apply friction impulse
    # -------------------------------------------------

    if inv_mass_a > 0.0:
        a.velocity.x -= friction_impulse.x * inv_mass_a
        a.velocity.y -= friction_impulse.y * inv_mass_a

    if inv_mass_b > 0.0:
        b.velocity.x += friction_impulse.x * inv_mass_b
        b.velocity.y += friction_impulse.y * inv_mass_b


def positional_correction(contact: Contact) -> None:
    """
    Applies positional correction to resolve penetration.

    Uses Baumgarte stabilization with slop to prevent jitter.

    Parameters:
    - percent: How much of the penetration to correct (0.8 = 80%)
    - slop: Penetration allowance to prevent micro-jitter
    """

    a = contact.a
    b = contact.b

    inv_mass_a = a.inv_mass
    inv_mass_b = b.inv_mass

    # Two static objects don't need correction
    if inv_mass_a + inv_mass_b == 0.0:
        return

    # -------------------------------------------------
    # Correction parameters
    # -------------------------------------------------

    percent = 0.8  # Correction strength (80%)
    slop = 0.01  # Penetration allowance (prevents jitter)

    # Only correct penetration beyond slop threshold
    correction_mag = max(contact.penetration - slop, 0.0)

    # Mass-weighted correction
    correction_mag /= inv_mass_a + inv_mass_b
    correction_mag *= percent

    # CRITICAL: Limit correction per iteration to prevent teleporting
    # For 1k-10k particles, this prevents solver instability
    MAX_CORRECTION_PER_ITERATION = 2.0  # Tune based on particle size
    correction_mag = min(correction_mag, MAX_CORRECTION_PER_ITERATION)

    correction = contact.normal * correction_mag

    # -------------------------------------------------
    # Apply positional correction
    # -------------------------------------------------

    if inv_mass_a > 0.0:
        a.position.x -= correction.x * inv_mass_a
        a.position.y -= correction.y * inv_mass_a

    if inv_mass_b > 0.0:
        b.position.x += correction.x * inv_mass_b
        b.position.y += correction.y * inv_mass_b


def solve_contact(contact: Contact) -> None:
    """
    Complete contact resolution: impulse + positional correction.
    """
    resolve_contact(contact)
    positional_correction(contact)
