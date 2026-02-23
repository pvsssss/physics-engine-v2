import pygame
import math
from engine.math.vec import Vec2
from engine.physics.particle import Particle


class InteractionHandler:
    """
    Handles mouse interactions for selecting and modifying particles in the scene.
    Operates strictly when the simulation is paused.
    """

    def __init__(self):
        self.selected_particle: Particle | None = None
        self.dragging_position = False
        self.dragging_velocity = False

        # Visual scaling factor for the velocity vector (matches renderer)
        self.velocity_display_scale = 0.1
        # Hitbox radius for the arrowhead control surface in pixels
        self.control_point_pixel_radius = 12

    def handle_event(
        self, event: pygame.event.Event, camera, psystem, sim_width: int
    ) -> bool:
        if event.type not in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            return False

        mouse_screen_x, mouse_screen_y = event.pos

        # Don't process clicks in the right-side configuration UI panel
        if mouse_screen_x > sim_width:
            if event.type == pygame.MOUSEBUTTONDOWN:
                return False

        world_x, world_y = camera.screen_to_world(mouse_screen_x, mouse_screen_y)
        mouse_world = Vec2(world_x, world_y)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 1. Check if we clicked the velocity vector control circle FIRST
            if self.selected_particle and self.selected_particle.alive:
                p = self.selected_particle
                ctrl_world_x = p.position.x + p.velocity.x * self.velocity_display_scale
                ctrl_world_y = p.position.y + p.velocity.y * self.velocity_display_scale

                # Check distance in screen space so the hitbox feels consistent regardless of camera zoom
                ctrl_screen_x, ctrl_screen_y = camera.world_to_screen(
                    ctrl_world_x, ctrl_world_y
                )
                dist_sq = (mouse_screen_x - ctrl_screen_x) ** 2 + (
                    mouse_screen_y - ctrl_screen_y
                ) ** 2

                if dist_sq <= self.control_point_pixel_radius**2:
                    self.dragging_velocity = True
                    return True

            # 2. Check if we clicked a particle (iterate in reverse to grab the top-most visual)
            for p in reversed(psystem.particles):
                if not p.alive:
                    continue

                dist_sq = (mouse_world.x - p.position.x) ** 2 + (
                    mouse_world.y - p.position.y
                ) ** 2
                if dist_sq <= p.radius**2:
                    self.selected_particle = p
                    self.dragging_position = True
                    # Clear sleep state so it immediately reacts when unpaused
                    p.sleeping = False
                    return True

            # Clicked empty space in the sim area
            if mouse_screen_x <= sim_width:
                self.selected_particle = None
            return False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_position = False
            self.dragging_velocity = False
            return False

        elif event.type == pygame.MOUSEMOTION:
            if (
                self.dragging_position
                and self.selected_particle
                and self.selected_particle.alive
            ):
                self.selected_particle.position.x = mouse_world.x
                self.selected_particle.position.y = mouse_world.y
                return True

            elif (
                self.dragging_velocity
                and self.selected_particle
                and self.selected_particle.alive
            ):
                # Update velocity based on mouse position relative to particle center
                dx_world = mouse_world.x - self.selected_particle.position.x
                dy_world = mouse_world.y - self.selected_particle.position.y

                self.selected_particle.velocity.x = (
                    dx_world / self.velocity_display_scale
                )
                self.selected_particle.velocity.y = (
                    dy_world / self.velocity_display_scale
                )
                return True

        return False
