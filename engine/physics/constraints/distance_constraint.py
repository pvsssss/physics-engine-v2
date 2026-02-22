from __future__ import annotations
from engine.physics.particle import Particle
from engine.physics.constraints.base_constraint import Constraint
from engine.math.vec import Vec2


class DistanceConstraint(Constraint):
    """
    Maintains a fixed distance between two particles (rope/stick).
    Uses iterative position-based constraint solving.
    """

    def __init__(
        self,
        particle_a: Particle,
        particle_b: Particle,
        distance: float | None = None,
        stiffness: float = 1.0,
    ):
        self.particle_a = particle_a
        self.particle_b = particle_b

        if distance is None:
            delta = particle_b.position - particle_a.position
            self.distance = delta.length()
        else:
            self.distance = distance

        self.stiffness = max(0.0, min(1.0, stiffness))

        # Store previous positions for velocity correction
        self.prev_pos_a = Vec2(particle_a.position.x, particle_a.position.y)
        self.prev_pos_b = Vec2(particle_b.position.x, particle_b.position.y)

    def solve(self, dt: float = 1.0 / 60.0) -> None:  # ADD dt parameter
        """
        Solve the distance constraint using position-based dynamics.
        """
        if not self.particle_a.alive or not self.particle_b.alive:
            return

        # Store positions before correction for velocity update
        prev_a = Vec2(self.particle_a.position.x, self.particle_a.position.y)
        prev_b = Vec2(self.particle_b.position.x, self.particle_b.position.y)

        # Calculate current distance
        delta = self.particle_b.position - self.particle_a.position
        current_distance = delta.length()

        if current_distance < 1e-8:
            return

        # Calculate constraint error
        error = current_distance - self.distance

        if abs(error) < 1e-6:
            return

        # Direction from A to B
        direction = delta / current_distance

        # Calculate correction based on inverse masses
        inv_mass_a = self.particle_a.inv_mass
        inv_mass_b = self.particle_b.inv_mass
        total_inv_mass = inv_mass_a + inv_mass_b

        if total_inv_mass < 1e-8:
            return

        # Apply stiffness
        correction_magnitude = error * self.stiffness

        # Calculate per-particle correction
        correction = direction * correction_magnitude

        # Apply position corrections proportional to inverse mass
        if inv_mass_a > 0.0:
            correction_a = correction * (inv_mass_a / total_inv_mass)
            self.particle_a.position.x += correction_a.x
            self.particle_a.position.y += correction_a.y

            if dt > 1e-8:
                pos_change_a = self.particle_a.position - prev_a
                self.particle_a.velocity.x += pos_change_a.x / dt
                self.particle_a.velocity.y += pos_change_a.y / dt

        if inv_mass_b > 0.0:
            correction_b = correction * (inv_mass_b / total_inv_mass)
            self.particle_b.position.x -= correction_b.x
            self.particle_b.position.y -= correction_b.y

            if dt > 1e-8:
                pos_change_b = self.particle_b.position - prev_b
                self.particle_b.velocity.x += pos_change_b.x / dt
                self.particle_b.velocity.y += pos_change_b.y / dt

    def get_particles(self) -> tuple[Particle, Particle]:
        return (self.particle_a, self.particle_b)
