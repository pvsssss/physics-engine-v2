"""
UI Framework for Physics Engine
Provides reusable UI components: buttons, panels, text, etc.
"""

import pygame
from typing import Callable, Optional, Tuple


class Button:
    """A clickable button with hover effects."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable] = None,
        font_size: int = 32,
        bg_color: Tuple[int, int, int] = (40, 80, 120),
        hover_color: Tuple[int, int, int] = (60, 100, 140),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        border_color: Tuple[int, int, int] = (100, 150, 200),
        border_width: int = 3,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font("assets/LilitaOne-Regular.ttf", font_size)

        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width

        self.hovered = False
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True

        return False

    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        if not self.enabled:
            color = (80, 80, 80)
        else:
            color = self.hover_color if self.hovered else self.bg_color

        # Draw button background
        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        # Draw border
        pygame.draw.rect(
            screen, self.border_color, self.rect, self.border_width, border_radius=8
        )

        # Draw crosshatch pattern (like in the images)
        self._draw_crosshatch(screen, self.rect)

        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def _draw_crosshatch(self, screen: pygame.Surface, rect: pygame.Rect):
        """Draw diagonal crosshatch pattern."""
        spacing = 15
        color = (50, 100, 150, 200)  # Semi-transparent

        # Create a surface with per-pixel alpha
        pattern = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Draw diagonal lines
        for i in range(-rect.height, rect.width + rect.height, spacing):
            start = (i, 0)
            end = (i + rect.height, rect.height)
            pygame.draw.line(pattern, color, start, end, 2)

        for i in range(-rect.height, rect.width + rect.height, spacing):
            start = (i, rect.height)
            end = (i + rect.height, 0)
            pygame.draw.line(pattern, color, start, end, 2)

        screen.blit(pattern, rect.topleft)


class Panel:
    """A rectangular panel/container."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        bg_color: Tuple[int, int, int] = (30, 30, 35),
        border_color: Tuple[int, int, int] = (100, 150, 200),
        border_width: int = 3,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width

    def draw(self, screen: pygame.Surface):
        """Draw the panel."""
        # Background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=0)

        # Border
        pygame.draw.rect(
            screen, self.border_color, self.rect, self.border_width, border_radius=0
        )


class SceneCard(Button):
    """A scene selection card with thumbnail and name."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        scene_name: str,
        scene_description: str,
        thumbnail: Optional[pygame.Surface] = None,
        callback: Optional[Callable] = None,
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            text="",  # We'll draw custom content
            callback=callback,
            font_size=24,
        )

        self.scene_name = scene_name
        self.scene_description = scene_description
        self.thumbnail = thumbnail
        self.title_font = pygame.font.Font("assets/LilitaOne-Regular.ttf", 28)
        self.desc_font = pygame.font.SysFont("consolas", 14)

    def draw(self, screen: pygame.Surface):
        """Draw the scene card."""
        color = self.hover_color if self.hovered else self.bg_color

        # Draw background
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        # Draw border
        pygame.draw.rect(
            screen, self.border_color, self.rect, self.border_width, border_radius=10
        )

        # Draw crosshatch pattern
        self._draw_crosshatch(screen, self.rect)

        # Draw thumbnail if available
        if self.thumbnail:
            thumb_rect = self.thumbnail.get_rect(
                center=(self.rect.centerx, self.rect.centery - 20)
            )
            screen.blit(self.thumbnail, thumb_rect)

        # Draw scene name
        name_surface = self.title_font.render(self.scene_name, True, self.text_color)
        name_rect = name_surface.get_rect(
            centerx=self.rect.centerx, bottom=self.rect.bottom - 15
        )
        screen.blit(name_surface, name_rect)


class Text:
    """Simple text renderer."""

    @staticmethod
    def draw(
        screen: pygame.Surface,
        text: str,
        x: int,
        y: int,
        font_size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        bold: bool = False,
        center: bool = False,
    ):
        """Draw text at position."""
        font = pygame.font.Font("assets/LilitaOne-Regular.ttf", font_size)
        text_surface = font.render(text, True, color)

        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, (x, y))

    @staticmethod
    def draw_title(
        screen: pygame.Surface,
        text: str,
        y: int,
        screen_width: int,
        font_size: int = 64,
        color: Tuple[int, int, int] = (255, 255, 255),
    ):
        """Draw centered title text."""
        Text.draw(
            screen,
            text,
            screen_width // 2,
            y,
            font_size=font_size,
            color=color,
            bold=True,
            center=True,
        )


class Slider:
    """A horizontal slider for adjusting values."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        min_val: float,
        max_val: float,
        initial_val: float,
        label: str = "",
        callback: Optional[Callable[[float], None]] = None,
    ):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.callback = callback

        self.dragging = False
        self.handle_radius = 10
        self.font = pygame.font.SysFont("consolas", 16)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_x = self._get_handle_x()
            handle_rect = pygame.Rect(
                handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2,
            )
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
            t = rel_x / self.rect.width
            self.value = self.min_val + t * (self.max_val - self.min_val)

            if self.callback:
                self.callback(self.value)
            return True

        return False

    def _get_handle_x(self) -> int:
        """Get the x position of the handle."""
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + t * self.rect.width)

    def draw(self, screen: pygame.Surface):
        """Draw the slider."""
        # Draw track
        pygame.draw.rect(screen, (60, 60, 70), self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 150, 200), self.rect, 2, border_radius=5)

        # Draw filled portion
        handle_x = self._get_handle_x()
        filled_rect = pygame.Rect(
            self.rect.x, self.rect.y, handle_x - self.rect.x, self.rect.height
        )
        pygame.draw.rect(screen, (80, 120, 160), filled_rect, border_radius=5)

        # Draw handle
        pygame.draw.circle(
            screen, (150, 200, 255), (handle_x, self.rect.centery), self.handle_radius
        )
        pygame.draw.circle(
            screen,
            (100, 150, 200),
            (handle_x, self.rect.centery),
            self.handle_radius,
            2,
        )

        # Draw label and value
        if self.label:
            label_text = f"{self.label}: {self.value:.2f}"
            text_surface = self.font.render(label_text, True, (200, 200, 200))
            screen.blit(text_surface, (self.rect.x, self.rect.y - 25))
