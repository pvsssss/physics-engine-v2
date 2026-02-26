"""
Scene Thumbnail Generators
Creates preview images for each physics scene.
"""

import pygame
import math


def generate_rope_thumbnail(width: int = 200, height: int = 150) -> pygame.Surface:
    """Generate thumbnail for rope scene."""
    surface = pygame.Surface((width, height))
    surface.fill((30, 30, 35))

    # Draw rope chain
    num_particles = 8
    particle_radius = 6
    spacing = 15

    start_x = width // 2
    start_y = 20

    # Draw particles and connections
    for i in range(num_particles):
        y = start_y + i * spacing

        # Draw connection line to next particle
        if i < num_particles - 1:
            next_y = start_y + (i + 1) * spacing
            pygame.draw.line(
                surface, (100, 150, 200), (start_x, y), (start_x, next_y), 2
            )

        # Draw particle
        color = (220, 220, 220) if i > 0 else (255, 100, 100)  # First is red (pinned)
        pygame.draw.circle(surface, color, (start_x, y), particle_radius)
        pygame.draw.circle(surface, (100, 150, 200), (start_x, y), particle_radius, 1)

    return surface


def generate_circle_container_thumbnail(
    width: int = 200, height: int = 150
) -> pygame.Surface:
    """Generate thumbnail for circle container scene."""
    surface = pygame.Surface((width, height))
    surface.fill((30, 30, 35))

    # Draw circle container
    center_x = width // 2
    center_y = height // 2
    radius = 60

    pygame.draw.circle(surface, (100, 150, 200), (center_x, center_y), radius, 2)

    # Draw particles inside
    import random

    random.seed(1)  # Consistent thumbnail

    for _ in range(12):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(10, radius - 15)
        x = int(center_x + math.cos(angle) * dist)
        y = int(center_y + math.sin(angle) * dist)

        pygame.draw.circle(surface, (220, 220, 220), (x, y), 5)
        pygame.draw.circle(surface, (100, 150, 200), (x, y), 5, 1)

    return surface


def generate_projectile_thumbnail(
    width: int = 200, height: int = 150
) -> pygame.Surface:
    """Generate thumbnail for projectile scene."""
    surface = pygame.Surface((width, height))
    surface.fill((30, 30, 35))

    # Draw parabolic trajectory
    points = []
    for i in range(40):
        t = i / 39.0
        x = 20 + t * (width - 40)
        # Parabola: y = -4 * height_scale * t * (t - 1)
        y = height - 20 - (4 * (height - 40) * t * (1 - t))
        points.append((int(x), int(y)))

    # Draw trail
    pygame.draw.lines(surface, (255, 100, 100), False, points, 2)

    # Draw particle at launch point
    pygame.draw.circle(surface, (220, 220, 220), points[0], 6)
    pygame.draw.circle(surface, (100, 150, 200), points[0], 6, 1)

    # Draw particle at peak
    peak_idx = len(points) // 2
    pygame.draw.circle(surface, (220, 220, 220), points[peak_idx], 6)
    pygame.draw.circle(surface, (100, 150, 200), points[peak_idx], 6, 1)

    # Draw scale markers at bottom
    for x in range(50, width - 20, 30):
        pygame.draw.line(surface, (80, 80, 90), (x, height - 10), (x, height - 5), 1)

    return surface


def generate_buoyancy_thumbnail(width: int = 200, height: int = 150) -> pygame.Surface:
    """Generate thumbnail for buoyancy scene."""
    surface = pygame.Surface((width, height))
    surface.fill((30, 30, 35))

    # Draw water
    water_y = int(height * 0.55)
    water_rect = pygame.Rect(0, water_y, width, height - water_y)

    # Water background with transparency
    water_surface = pygame.Surface((width, height - water_y))
    water_surface.fill((50, 120, 200))
    water_surface.set_alpha(128)
    surface.blit(water_surface, (0, water_y))

    # Water surface line
    pygame.draw.line(surface, (100, 150, 220), (0, water_y), (width, water_y), 2)

    # Draw particles at different depths
    # Red particle - floating at surface
    pygame.draw.circle(surface, (255, 50, 50), (50, water_y - 8), 6)
    pygame.draw.circle(surface, (200, 40, 40), (50, water_y - 8), 6, 1)

    # Purple particle - neutral buoyancy (mid-water)
    pygame.draw.circle(surface, (150, 50, 200), (100, water_y + 30), 6)
    pygame.draw.circle(surface, (120, 40, 160), (100, water_y + 30), 6, 1)

    # Blue particle - sinking (near bottom)
    pygame.draw.circle(surface, (50, 100, 255), (150, water_y + 60), 6)
    pygame.draw.circle(surface, (40, 80, 200), (150, water_y + 60), 6, 1)

    # Another red particle floating
    pygame.draw.circle(surface, (255, 50, 50), (120, water_y - 5), 5)

    # Another blue particle sinking
    pygame.draw.circle(surface, (50, 100, 255), (70, water_y + 50), 5)

    return surface


# Scene information registry
SCENE_INFO = [
    {
        "name": "Rope Simulation",
        "description": "Connected particles with constraints",
        "thumbnail_func": generate_rope_thumbnail,
        "scene_module": "rope_scene",
    },
    {
        "name": "Collision Lab",
        "description": "Particles in circular boundary",
        "thumbnail_func": generate_circle_container_thumbnail,
        "scene_module": "circle_container_scene",
    },
    {
        "name": "Projectile Motion",
        "description": "Ballistic trajectory simulation",
        "thumbnail_func": generate_projectile_thumbnail,
        "scene_module": "projectile_scene",
    },
    {
        "name": "Buoyancy",
        "description": "Floating and sinking in water",
        "thumbnail_func": generate_buoyancy_thumbnail,
        "scene_module": "buoyancy_scene",
    },
]
