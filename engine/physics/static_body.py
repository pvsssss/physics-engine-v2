from __future__ import annotations

from engine.math.vec import Vec2


class StaticBody:
    """
    Represents an immovable collision body with infinite mass.
    Used for world boundaries and containers
    """

    __slots__ = ()

    # default values
    inv_mass: float = 0.0
    velocity: Vec2 = Vec2(0.0, 0.0)
    restitution: float = 0.8
    friction: float = 0.1
    alive: bool = True
