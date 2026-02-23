import pygame
from engine.render.render_config import *
from engine.render.camera import Camera
import pygame.gfxdraw

from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.containers.circle_container import CircleContainer


class PygameRenderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("2D Physics Engine")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)
        self.small_font = pygame.font.SysFont("consolas", 12)

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, PIXELS_PER_UNIT)

        # Debug toggles
        self.draw_velocities = False
        self.draw_constraints = True
        self.draw_contacts = False
        self.draw_grid = True
        self.draw_containers = True

        # Trajectory tracking
        self.trajectory_trails = {}  # particle_id -> list of positions
        self.draw_trajectories = False
        self.draw_coordinates = False
        self.draw_scale = False

        # Coordinate system mode for projectile/buoyancy scenes
        # self.use_bottom_left_origin = True

        # Water region rendering
        self.draw_water = False
        self.water_region = None  # (x, y, width, height) in screen coords

    def begin_frame(self):
        self.screen.fill(BACKGROUND_COLOR)

    def end_frame(self, fps=None):
        if fps is not None:
            self._draw_text(f"FPS: {int(fps)}", 10, 10)

        pygame.display.flip()

    def tick(self, target_fps=60):
        return self.clock.tick(target_fps)

    def draw_particle(self, particle, custom_color=None):
        """
        Draw a particle. If particle has a 'color' attribute, use it.
        Otherwise use default colors based on sleeping state.
        """
        # Check if particle has custom color attribute
        if hasattr(particle, "color") and particle.color is not None:
            color = particle.color
        elif custom_color is not None:
            color = custom_color
        else:
            color = SLEEPING_PARTICLE_COLOR if particle.sleeping else PARTICLE_COLOR

        x, y = self.camera.world_to_screen(particle.position.x, particle.position.y)

        radius = int(particle.radius * self.camera.pixels_per_unit)

        pygame.gfxdraw.aacircle(self.screen, x, y, radius, color)
        pygame.gfxdraw.filled_circle(self.screen, x, y, radius, color)

        if self.draw_velocities:
            self._draw_velocity(particle)

    def draw_constraint(self, p1, p2):
        x1, y1 = self.camera.world_to_screen(p1.position.x, p1.position.y)
        x2, y2 = self.camera.world_to_screen(p2.position.x, p2.position.y)

        pygame.draw.line(self.screen, CONSTRAINT_COLOR, (x1, y1), (x2, y2), 2)

    def draw_contact(self, contact):
        px, py = self.camera.world_to_screen(contact.point.x, contact.point.y)

        nx, ny = contact.normal.x, contact.normal.y
        scale = 20

        pygame.draw.circle(self.screen, CONTACT_COLOR, (px, py), 4)

        pygame.draw.line(
            self.screen,
            CONTACT_COLOR,
            (px, py),
            (px + int(nx * scale), py + int(ny * scale)),
            2,
        )

    # debugging
    def draw_grid(self, cell_size):
        if not self.draw_grid:
            return

        size = int(cell_size * self.camera.pixels_per_unit)

        for x in range(0, SCREEN_WIDTH, size):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))

        for y in range(0, SCREEN_HEIGHT, size):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

    def _draw_velocity(self, particle):
        x, y = self.camera.world_to_screen(particle.position.x, particle.position.y)

        vx = particle.velocity.x * 0.1
        vy = particle.velocity.y * 0.1

        pygame.draw.line(
            self.screen, VELOCITY_COLOR, (x, y), (x + int(vx), y + int(vy)), 2
        )

    def _draw_text(self, text, x, y, font=None, color=(200, 200, 200)):
        if font is None:
            font = self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw_container_bounds(self, container):
        """Debug: Draw container rectangle"""
        if not self.draw_constraint:
            return
        x1, y1 = self.camera.world_to_screen(container.min.x, container.min.y)
        x2, y2 = self.camera.world_to_screen(container.max.x, container.max.y)

        width = x2 - x1
        height = y2 - y1

        pygame.draw.rect(self.screen, (255, 0, 0), (x1, y1, width, height), 1)
        # Draw text showing bounds
        self._draw_text(
            f"Container: {container.min.x},{container.min.y} to {container.max.x},{container.max.y}",
            10,
            30,
        )

    def draw_container(self, container):
        """Draw container based on its type"""
        if isinstance(container, RectangleContainer) and self.draw_containers == True:
            self._draw_rectangle_container(container)
        elif isinstance(container, CircleContainer) and self.draw_containers == True:
            self._draw_circle_container(container)

    def _draw_rectangle_container(self, container):
        """Draw rectangular container bounds"""
        x1, y1 = self.camera.world_to_screen(container.min.x, container.min.y)
        x2, y2 = self.camera.world_to_screen(container.max.x, container.max.y)
        width = x2 - x1
        height = y2 - y1
        pygame.draw.rect(self.screen, CONTAINER_COLOR, (x1, y1, width, height), 1)

    def _draw_circle_container(self, container):
        """Draw circular container bounds"""
        cx, cy = self.camera.world_to_screen(container.center.x, container.center.y)
        radius = int(container.radius * self.camera.pixels_per_unit)
        # Draw 1-2 pixels larger to prevent visual clipping
        pygame.gfxdraw.aacircle(self.screen, cx, cy, radius, CONTAINER_COLOR)

    # ========================================
    # COORDINATE CONVERSION HELPERS
    # ========================================

    # def _engine_to_display_coords(self, x, y):
    #     """
    #     Convert engine coordinates to display coordinates.
    #     If using bottom-left origin, converts from top-left to bottom-left.
    #     Otherwise returns coordinates as-is.
    #     """
    #     if self.use_bottom_left_origin:
    #         return (x, SCREEN_HEIGHT - y)
    #     return (x, y)

    # ========================================
    # BUOYANCY SCENE FEATURES
    # ========================================

    def draw_water_region(
        self,
        water_top,
        water_bottom,
        water_color=(50, 120, 200, 128),
        surface_color=(100, 150, 220),
    ):
        """
        Draw a water region as a filled rectangle.

        Args:
            water_top: Y-coordinate of water surface (engine coords, top-left origin)
            water_bottom: Y-coordinate of water bottom (engine coords, top-left origin)
            water_color: RGBA color for water body (with alpha for transparency)
            surface_color: RGB color for water surface line
        """
        if not self.draw_water:
            return

        # Convert to screen coordinates
        x1, y1 = self.camera.world_to_screen(0, water_top)
        x2, y2 = self.camera.world_to_screen(SCREEN_WIDTH, water_bottom)

        width = x2 - x1
        height = y2 - y1

        # Create a surface with alpha for water transparency
        water_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        water_surface.fill(water_color)

        # Draw water body
        self.screen.blit(water_surface, (x1, y1))

        # Draw water surface line (more visible)
        pygame.draw.line(self.screen, surface_color, (0, y1), (SCREEN_WIDTH, y1), 3)

    def draw_density_legend(
        self, x, y, low_color, mid_color, high_color, min_density, max_density
    ):
        """
        Draw a color gradient legend showing density mapping.

        Args:
            x, y: Top-left position of legend
            low_color, mid_color, high_color: RGB tuples for gradient
            min_density, max_density: Density range
        """
        legend_width = 200
        legend_height = 30

        # Draw background
        pygame.draw.rect(
            self.screen,
            (40, 40, 50),
            (x - 5, y - 5, legend_width + 10, legend_height + 45),
        )

        # Draw gradient bar
        for i in range(legend_width):
            t = i / legend_width

            if t < 0.5:
                # First half: low to mid
                local_t = t * 2.0
                r = int(low_color[0] + (mid_color[0] - low_color[0]) * local_t)
                g = int(low_color[1] + (mid_color[1] - low_color[1]) * local_t)
                b = int(low_color[2] + (mid_color[2] - low_color[2]) * local_t)
            else:
                # Second half: mid to high
                local_t = (t - 0.5) * 2.0
                r = int(mid_color[0] + (high_color[0] - mid_color[0]) * local_t)
                g = int(mid_color[1] + (high_color[1] - mid_color[1]) * local_t)
                b = int(mid_color[2] + (high_color[2] - mid_color[2]) * local_t)

            pygame.draw.line(
                self.screen, (r, g, b), (x + i, y), (x + i, y + legend_height), 2
            )

        # Draw border
        pygame.draw.rect(
            self.screen, (150, 150, 150), (x, y, legend_width, legend_height), 2
        )

        # Draw labels
        self._draw_text("Density:", x, y - 20, font=self.small_font)
        self._draw_text(
            f"{min_density:.0f}", x, y + legend_height + 5, font=self.small_font
        )
        self._draw_text(
            "(floats)",
            x,
            y + legend_height + 20,
            font=self.small_font,
            color=(150, 150, 150),
        )

        mid_x = x + legend_width // 2 - 20
        self._draw_text(
            f"{(min_density + max_density) / 2:.0f}",
            mid_x,
            y + legend_height + 5,
            font=self.small_font,
        )

        max_x = x + legend_width - 40
        self._draw_text(
            f"{max_density:.0f}", max_x, y + legend_height + 5, font=self.small_font
        )
        self._draw_text(
            "(sinks)",
            max_x,
            y + legend_height + 20,
            font=self.small_font,
            color=(150, 150, 150),
        )

    # ========================================
    # PROJECTILE MOTION FEATURES
    # ========================================

    def track_particle_trajectory(
        self, particle, max_points=1000, trajectory_color=(255, 100, 100)
    ):
        """
        Adds current particle position to trajectory trail.
        Call this once per frame for each particle you want to track.
        """
        if not self.draw_trajectories:
            return

        particle_id = id(particle)

        if particle_id not in self.trajectory_trails:
            self.trajectory_trails[particle_id] = []

        trail = self.trajectory_trails[particle_id]
        trail.append((particle.position.x, particle.position.y))

        # Limit trail length to prevent memory issues
        if len(trail) > max_points:
            trail.pop(0)

    def draw_trajectory_trail(self, particle, trajectory_color=(255, 100, 100)):
        """
        Draws the trajectory trail for a particle.
        """
        if not self.draw_trajectories:
            return

        particle_id = id(particle)
        if particle_id not in self.trajectory_trails:
            return

        trail = self.trajectory_trails[particle_id]
        if len(trail) < 2:
            return

        # Convert all trail points to screen coordinates
        screen_points = [self.camera.world_to_screen(x, y) for x, y in trail]

        # Draw the trail as a series of lines
        pygame.draw.lines(self.screen, trajectory_color, False, screen_points, 2)

    def draw_particle_coordinates(self, particle, coord_color=(200, 200, 200)):
        if not self.draw_coordinates:
            return
        x, y = self.camera.world_to_screen(particle.position.x, particle.position.y)

        # Print native coordinates directly
        coord_text = f"({particle.position.x:.1f}, {particle.position.y:.1f})"
        text_surface = self.small_font.render(coord_text, True, coord_color)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()

        offset_y = int(particle.radius * self.camera.pixels_per_unit) + 5

        # If particle is near bottom of screen (Screen Y near height), show coordinates above
        if y + offset_y + text_height > SCREEN_HEIGHT - 10:
            text_y = y - offset_y - text_height
        else:
            text_y = y + offset_y

        text_x = max(5, min(x - text_width // 2, SCREEN_WIDTH - text_width - 5))
        text_y = max(5, min(text_y, SCREEN_HEIGHT - text_height - 5))
        self.screen.blit(text_surface, (text_x, text_y))

    def draw_scale_markers(self, tick_interval=100.0, scale_color=(150, 150, 150)):
        if not self.draw_scale:
            return

        y_bottom = SCREEN_HEIGHT - 2
        world_x_start = self.camera.offset_x
        world_x_end = world_x_start + SCREEN_WIDTH / self.camera.pixels_per_unit

        x_pos = int(world_x_start / tick_interval) * tick_interval
        while x_pos <= world_x_end:
            screen_x, _ = self.camera.world_to_screen(x_pos, 0)
            if 0 <= screen_x <= SCREEN_WIDTH:
                pygame.draw.line(
                    self.screen,
                    scale_color,
                    (screen_x, y_bottom - 10),
                    (screen_x, y_bottom),
                    2,
                )
                text_surface = self.small_font.render(
                    f"{int(x_pos)}", True, scale_color
                )
                self.screen.blit(
                    text_surface,
                    (screen_x - text_surface.get_width() // 2, y_bottom - 25),
                )
            x_pos += tick_interval

        x_left = 0
        world_y_start = self.camera.offset_y
        world_y_end = world_y_start + self.camera.height / self.camera.pixels_per_unit

        y_pos = int(world_y_start / tick_interval) * tick_interval
        while y_pos <= world_y_end:
            _, screen_y = self.camera.world_to_screen(0, y_pos)
            if 0 <= screen_y <= SCREEN_HEIGHT:
                pygame.draw.line(
                    self.screen,
                    scale_color,
                    (x_left + 2, screen_y),
                    (x_left + 12, screen_y),
                    2,
                )
                text_surface = self.small_font.render(
                    f"{int(y_pos)}", True, scale_color
                )
                self.screen.blit(text_surface, (x_left + 17, max(0, screen_y - 6)))
            y_pos += tick_interval

    def clear_trajectories(self):
        """Clears all trajectory trails."""
        self.trajectory_trails.clear()

    def draw_particle_highlight(self, particle):
        """Draws a bright yellow antialiased highlight ring around the selected particle."""
        if not particle.alive:
            return

        x, y = self.camera.world_to_screen(particle.position.x, particle.position.y)
        radius = int(particle.radius * self.camera.pixels_per_unit)

        highlight_color = (255, 255, 0)

        pygame.draw.circle(self.screen, highlight_color, (x, y), radius, 2)
        # Draw 3 concentric antialiased circles to simulate a line thickness of 3
        # for offset in (2, 3, 4):
        #     pygame.gfxdraw.aacircle(self.screen, x, y, radius + offset, highlight_color)

    def draw_velocity_control(self, particle):
        """Draws the interactive velocity vector and control circle."""
        if not particle.alive:
            return
        import math

        # 1. Calculate the start and end points in mathematical WORLD space first
        start_world_x = particle.position.x
        start_world_y = particle.position.y

        # Scale matches the interaction handler (0.1)
        end_world_x = start_world_x + particle.velocity.x * 0.1
        end_world_y = start_world_y + particle.velocity.y * 0.1

        # 2. Convert BOTH points cleanly to screen space
        x, y = self.camera.world_to_screen(start_world_x, start_world_y)
        end_x, end_y = self.camera.world_to_screen(end_world_x, end_world_y)

        # Draw bright green line
        pygame.draw.line(self.screen, (0, 255, 0), (x, y), (end_x, end_y), 3)

        # Calculate screen-space angle for the arrowhead
        screen_dx = end_x - x
        screen_dy = end_y - y
        angle = math.atan2(screen_dy, screen_dx)

        arrow_len = 14
        a1 = angle + math.pi * 0.8
        a2 = angle - math.pi * 0.8

        pt1 = (end_x + math.cos(a1) * arrow_len, end_y + math.sin(a1) * arrow_len)
        pt2 = (end_x + math.cos(a2) * arrow_len, end_y + math.sin(a2) * arrow_len)
        pygame.draw.polygon(self.screen, (0, 255, 0), [(end_x, end_y), pt1, pt2])

        # Draw the translucent white control circle (120 out of 255 alpha)
        pygame.gfxdraw.filled_circle(
            self.screen, end_x, end_y, 10, (255, 255, 255, 120)
        )
        # Draw a slightly transparent black outline for it
        pygame.gfxdraw.aacircle(self.screen, end_x, end_y, 10, (0, 0, 0, 200))

        # Draw 'v' text
        text_surface = self.small_font.render("v", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(end_x, end_y))
        self.screen.blit(text_surface, text_rect)

    def draw_playback_indicator(self, is_paused: bool):
        """Draws a translucent Play/Pause icon at the top center of the screen."""
        sim_width = self.screen.get_width()
        x, y = 40, 10

        # # Draw a translucent dark background circle
        # pygame.gfxdraw.filled_circle(self.screen, x, y, 24, (0, 0, 0, 100))
        # pygame.gfxdraw.aacircle(self.screen, x, y, 24, (200, 200, 200, 150))

        icon_color = (255, 255, 255, 200)

        if is_paused:
            # # Draw Pause icon (two vertical bars)
            # pygame.gfxdraw.box(
            #     self.screen, pygame.Rect(x - 8, y - 10, 6, 20), icon_color
            # )
            # pygame.gfxdraw.box(
            #     self.screen, pygame.Rect(x + 2, y - 10, 6, 20), icon_color
            # )

            # Add small "PAUSED" text below it
            text_surface = self.font.render("PAUSED", True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(x, y + 35))
            self.screen.blit(text_surface, text_rect)
        else:
            # Draw Play icon (triangle)
            text_surface = self.font.render("PLAYING", True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(x, y + 35))
            self.screen.blit(text_surface, text_rect)
            # pts = [(x - 4, y - 10), (x - 4, y + 10), (x + 10, y)]
            # pygame.gfxdraw.filled_polygon(self.screen, pts, icon_color)
            # pygame.gfxdraw.aapolygon(self.screen, pts, icon_color)
