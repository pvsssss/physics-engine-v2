import pygame
from engine.render.render_config import *
from engine.render.camera import Camera

from engine.physics.containers.rectangle_container import RectangleContainer
from engine.physics.containers.circle_container import CircleContainer

# import pygame.gfxdraw


class PygameRenderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("2D Physics Engine")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, PIXELS_PER_UNIT)

        # Debug toggles
        self.draw_velocities = False
        self.draw_constraints = False
        self.draw_contacts = False
        self.draw_grid = True

    def begin_frame(self):
        self.screen.fill(BACKGROUND_COLOR)

    def end_frame(self, fps=None):
        if fps is not None:
            self._draw_text(f"FPS: {int(fps)}", 10, 10)

        pygame.display.flip()

    def tick(self, target_fps=60):
        return self.clock.tick(target_fps)

    def draw_particle(self, particle):
        color = SLEEPING_PARTICLE_COLOR if particle.sleeping else PARTICLE_COLOR

        x, y = self.camera.world_to_screen(particle.position.x, particle.position.y)

        radius = int(particle.radius * self.camera.pixels_per_unit)

        pygame.draw.circle(self.screen, color, (x, y), radius)

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

    def _draw_text(self, text, x, y):
        surface = self.font.render(text, True, (200, 200, 200))
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
        if isinstance(container, RectangleContainer):
            self._draw_rectangle_container(container)
        elif isinstance(container, CircleContainer):
            self._draw_circle_container(container)

    def _draw_rectangle_container(self, container):
        """Draw rectangular container bounds"""
        x1, y1 = self.camera.world_to_screen(container.min.x, container.min.y)
        x2, y2 = self.camera.world_to_screen(container.max.x, container.max.y)
        width = x2 - x1
        height = y2 - y1
        pygame.draw.rect(self.screen, CONSTRAINT_COLOR, (x1, y1, width, height), 2)

    def _draw_circle_container(self, container):
        """Draw circular container bounds"""
        cx, cy = self.camera.world_to_screen(container.center.x, container.center.y)
        radius = int(container.radius * self.camera.pixels_per_unit)
        # Draw 1-2 pixels larger to prevent visual clipping
        pygame.draw.circle(self.screen, CONSTRAINT_COLOR, (cx, cy), radius + 1, 2)
