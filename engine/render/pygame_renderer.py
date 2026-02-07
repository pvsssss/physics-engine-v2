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
        self.use_bottom_left_origin = False

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
        pygame.draw.rect(self.screen, CONTAINER_COLOR, (x1, y1, width, height), 2)

    def _draw_circle_container(self, container):
        """Draw circular container bounds"""
        cx, cy = self.camera.world_to_screen(container.center.x, container.center.y)
        radius = int(container.radius * self.camera.pixels_per_unit)
        # Draw 1-2 pixels larger to prevent visual clipping
        pygame.gfxdraw.aacircle(self.screen, cx, cy, radius, CONTAINER_COLOR)

    # ========================================
    # COORDINATE CONVERSION HELPERS
    # ========================================

    def _engine_to_display_coords(self, x, y):
        """
        Convert engine coordinates to display coordinates.
        If using bottom-left origin, converts from top-left to bottom-left.
        Otherwise returns coordinates as-is.
        """
        if self.use_bottom_left_origin:
            return (x, SCREEN_HEIGHT - y)
        return (x, y)

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
        """
        Draws the coordinates of the particle following it.
        Displays below particle if on screen, above if not.
        For projectile scene, shows coordinates in bottom-left origin system.
        """
        if not self.draw_coordinates:
            return

        x, y = self.camera.world_to_screen(particle.position.x, particle.position.y)

        # Convert to display coordinates (bottom-left origin for projectile scene)
        display_x, display_y = self._engine_to_display_coords(
            particle.position.x, particle.position.y
        )

        # Format coordinates
        coord_text = f"({display_x:.1f}, {display_y:.1f})"
        text_surface = self.small_font.render(coord_text, True, coord_color)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()

        # Determine position (below particle by default, above if near bottom)
        offset_y = int(particle.radius * self.camera.pixels_per_unit) + 5

        # If particle is near bottom of screen, show coordinates above
        if y + offset_y + text_height > SCREEN_HEIGHT - 10:
            text_y = y - offset_y - text_height
        else:
            text_y = y + offset_y

        # Center text horizontally under particle
        text_x = x - text_width // 2

        # Clamp to screen bounds
        text_x = max(5, min(text_x, SCREEN_WIDTH - text_width - 5))
        text_y = max(5, min(text_y, SCREEN_HEIGHT - text_height - 5))

        self.screen.blit(text_surface, (text_x, text_y))

    def draw_scale_markers(self, tick_interval=100.0, scale_color=(150, 150, 150)):
        """
        Draws scale markers on the left and bottom edges of the screen.
        Shows world coordinates at regular intervals.
        For projectile scene, shows coordinates with bottom-left origin (0,0).
        """
        if not self.draw_scale:
            return

        # Bottom scale (X-axis)
        y_bottom = SCREEN_HEIGHT - 1

        # Find the range of world coordinates visible
        world_x_start = self.camera.offset_x
        world_x_end = world_x_start + SCREEN_WIDTH / self.camera.pixels_per_unit

        # Draw tick marks at intervals
        tick_start = int(world_x_start / tick_interval) * tick_interval
        x_pos = tick_start

        while x_pos <= world_x_end:
            screen_x, _ = self.camera.world_to_screen(x_pos, 0)

            if 0 <= screen_x <= SCREEN_WIDTH:
                # Draw tick mark
                pygame.draw.line(
                    self.screen,
                    scale_color,
                    (screen_x, y_bottom - 10),
                    (screen_x, y_bottom),
                    2,
                )

                # For bottom-left origin, X coordinate stays the same
                display_x = x_pos if self.use_bottom_left_origin else x_pos
                label = f"{int(display_x)}"
                text_surface = self.small_font.render(label, True, scale_color)
                text_width = text_surface.get_width()
                self.screen.blit(
                    text_surface, (screen_x - text_width // 2, y_bottom - 25)
                )

            x_pos += tick_interval

        # Left scale (Y-axis)
        x_left = 0

        world_y_start = self.camera.offset_y
        world_y_end = world_y_start + SCREEN_HEIGHT / self.camera.pixels_per_unit

        tick_start = int(world_y_start / tick_interval) * tick_interval
        y_pos = tick_start

        while y_pos <= world_y_end:
            _, screen_y = self.camera.world_to_screen(0, y_pos)

            if 0 <= screen_y <= SCREEN_HEIGHT:
                # Draw tick mark
                pygame.draw.line(
                    self.screen,
                    scale_color,
                    (x_left, screen_y),
                    (x_left + 10, screen_y),
                    2,
                )

                # Convert Y coordinate for display
                if self.use_bottom_left_origin:
                    display_y = SCREEN_HEIGHT - y_pos
                else:
                    display_y = y_pos

                label = f"{int(display_y)}"
                text_surface = self.small_font.render(label, True, scale_color)
                self.screen.blit(text_surface, (x_left + 15, screen_y - 8))

            y_pos += tick_interval

    def clear_trajectories(self):
        """Clears all trajectory trails."""
        self.trajectory_trails.clear()
