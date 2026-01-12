from __future__ import annotations
import math

from engine.math.vec import Vec2
from engine.physics.particle import Particle
from engine.physics.contact import Contact


# Small epsilon for floating-point comparisons
EPSILON = 1e-8


def circle_circle(a: Particle, b: Particle) -> Contact | None:
    """
    Narrowphase collision detection between two circular particles.

    Returns a Contact if the particles overlap, otherwise None.

    Algorithm:
    1. Compute distance between centers
    2. Check if distance < sum of radii (overlap test)
    3. Compute collision normal and penetration depth
    4. Handle edge case of coincident centers
    """

    delta = b.position - a.position
    dist_sq = delta.length_squared()

    radius_sum = a.radius + b.radius
    radius_sum_sq = radius_sum * radius_sum

    # Early out if no collision
    if dist_sq >= radius_sum_sq:
        return None

    # Two static particles don't need collision response
    if a.inv_mass == 0.0 and b.inv_mass == 0.0:
        return None

    # Handle coincident centers (rare but critical edge case)
    if dist_sq < EPSILON * EPSILON:
        # Centers are essentially at the same position
        # Use arbitrary normal
        normal = Vec2(1.0, 0.0)
        penetration = radius_sum
        contact_point = a.position.copy()
    else:
        # Normal case where circles overlap but centers are distinct
        distance = math.sqrt(dist_sq)
        normal = delta / distance  # Unit vector from A to B
        penetration = radius_sum - distance

        # Contact point at the midpoint of penetration
        # (on surface of A, halfway into the overlap)
        contact_point = a.position + normal * (a.radius - penetration * 0.5)

    return Contact(
        a=a,
        b=b,
        normal=normal,
        penetration=penetration,
        contact_points=[contact_point],
    )
