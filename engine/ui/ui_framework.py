"""
UI Framework for Physics Engine
Provides reusable UI components: buttons, panels, text, sliders, text inputs, and scroll areas.
"""

import pygame
import time
from typing import Callable, Optional, Tuple, Union


class Widget:
    """Base class for all UI components to guarantee consistent scrolling."""

    def __init__(self):
        if not hasattr(self, "rect"):
            self.rect = pygame.Rect(0, 0, 0, 0)

    def shift_y(self, dy: int):
        self.rect.y += dy

    def set_y(self, y: int):
        self.shift_y(y - self.rect.y)


class Button(Widget):
    """A clickable button with hover and press visual effects."""

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
        try:
            self.font = pygame.font.Font("assets/LilitaOne-Regular.ttf", font_size)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("impact", font_size)

        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.hovered = False
        self.pressed = False
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            if not self.hovered:
                self.pressed = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.hovered:
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
        return False

    def draw(self, screen: pygame.Surface):
        color = (
            (80, 80, 80)
            if not self.enabled
            else (self.hover_color if self.hovered else self.bg_color)
        )
        if self.pressed:
            color = (
                max(0, color[0] - 20),
                max(0, color[1] - 20),
                max(0, color[2] - 20),
            )

        y_offset = 3 if self.pressed else 0
        draw_rect = self.rect.move(0, y_offset)

        pygame.draw.rect(screen, color, draw_rect, border_radius=8)
        pygame.draw.rect(
            screen, self.border_color, draw_rect, self.border_width, border_radius=8
        )
        self._draw_crosshatch(screen, draw_rect)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        screen.blit(text_surface, text_rect)

    def _draw_crosshatch(self, screen: pygame.Surface, rect: pygame.Rect):
        spacing, color = 15, (50, 100, 150, 200)
        pattern = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for i in range(-rect.height, rect.width + rect.height, spacing):
            pygame.draw.line(pattern, color, (i, 0), (i + rect.height, rect.height), 2)
        for i in range(-rect.height, rect.width + rect.height, spacing):
            pygame.draw.line(pattern, color, (i, rect.height), (i + rect.height, 0), 2)
        screen.blit(pattern, rect.topleft)


class Panel(Widget):
    """A rectangular panel/container."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        bg_color=(30, 30, 35),
        border_color=(100, 150, 200),
        border_width=3,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=0)
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
        thumbnail=None,
        callback=None,
    ):
        super().__init__(x, y, width, height, text="", callback=callback, font_size=24)
        self.scene_name = scene_name
        self.scene_description = scene_description
        self.thumbnail = thumbnail
        try:
            self.title_font = pygame.font.Font("assets/LilitaOne-Regular.ttf", 28)
        except FileNotFoundError:
            self.title_font = pygame.font.SysFont("impact", 28)

    def draw(self, screen: pygame.Surface):
        color = self.hover_color if self.hovered else self.bg_color
        if self.pressed:
            color = (
                max(0, color[0] - 20),
                max(0, color[1] - 20),
                max(0, color[2] - 20),
            )

        y_offset = 3 if self.pressed else 0
        draw_rect = self.rect.move(0, y_offset)

        pygame.draw.rect(screen, color, draw_rect, border_radius=10)
        pygame.draw.rect(
            screen, self.border_color, draw_rect, self.border_width, border_radius=10
        )
        self._draw_crosshatch(screen, draw_rect)

        if self.thumbnail:
            thumb_rect = self.thumbnail.get_rect(
                center=(draw_rect.centerx, draw_rect.centery - 20)
            )
            screen.blit(self.thumbnail, thumb_rect)

        name_surface = self.title_font.render(self.scene_name, True, self.text_color)
        name_rect = name_surface.get_rect(
            centerx=draw_rect.centerx, bottom=draw_rect.bottom - 15
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
        color=(255, 255, 255),
        bold=False,
        center=False,
    ):
        try:
            font = pygame.font.Font("assets/LilitaOne-Regular.ttf", font_size)
        except FileNotFoundError:
            font = pygame.font.SysFont("impact", font_size)
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
        color=(255, 255, 255),
    ):
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


class Slider(Widget):
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
        callback=None,
    ):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.value = float(initial_val)
        self.label = label
        self.callback = callback
        self.dragging = False
        self.handle_radius = 10
        self.font = pygame.font.SysFont("consolas", 14)

    def set_value(self, new_val: float):
        self.value = max(self.min_val, min(self.max_val, float(new_val)))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_x = self._get_handle_x()
            handle_rect = pygame.Rect(
                handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2,
            )
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_pos(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value_from_pos(event.pos[0])
            return True
        return False

    def _update_value_from_pos(self, mouse_x: int):
        rel_x = max(0, min(mouse_x - self.rect.x, self.rect.width))
        t = rel_x / self.rect.width if self.rect.width > 0 else 0
        self.value = self.min_val + t * (self.max_val - self.min_val)
        if self.callback:
            self.callback(self.value)

    def _get_handle_x(self) -> int:
        t = (
            0
            if self.max_val == self.min_val
            else (self.value - self.min_val) / (self.max_val - self.min_val)
        )
        return int(self.rect.x + t * self.rect.width)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (60, 60, 70), self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 150, 200), self.rect, 2, border_radius=5)
        handle_x = self._get_handle_x()
        filled_rect = pygame.Rect(
            self.rect.x, self.rect.y, max(0, handle_x - self.rect.x), self.rect.height
        )
        pygame.draw.rect(screen, (80, 120, 160), filled_rect, border_radius=5)
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
        if self.label:
            text_surface = self.font.render(
                f"{self.label}: {self.value:.2f}", True, (200, 200, 200)
            )
            screen.blit(text_surface, (self.rect.x, self.rect.y - 20))


class TextInput(Widget):
    """A text input field that properly handles its own rendering and bounds."""

    # Class-level tracker for the globally active input
    active_input = None

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        initial_text: str = "",
        numeric_only: bool = False,
        callback=None,
        font_size: int = 16,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = str(initial_text)
        self.numeric_only = numeric_only
        self.callback = callback
        self.font = pygame.font.SysFont("consolas", font_size)
        self.active = False
        self.cursor_visible = True
        self.last_blink_time = time.time()
        self.color_active = (100, 150, 200)
        self.color_inactive = (60, 60, 70)
        self.color_bg = (20, 20, 25)
        self.color_text = (220, 220, 220)

    def get_value(self) -> Union[str, float]:
        if self.numeric_only:
            try:
                return float(self.text) if self.text else 0.0
            except ValueError:
                return 0.0
        return self.text

    def set_value(self, val):
        self.text = (
            f"{val:.2f}" if self.numeric_only and isinstance(val, float) else str(val)
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)

            if self.active:
                if TextInput.active_input and TextInput.active_input != self:
                    TextInput.active_input.active = False
                    if TextInput.active_input.callback:
                        TextInput.active_input.callback(
                            TextInput.active_input.get_value()
                        )
                TextInput.active_input = self
            else:
                if was_active:
                    if TextInput.active_input == self:
                        TextInput.active_input = None
                    if self.callback:
                        self.callback(self.get_value())

            return self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                if TextInput.active_input == self:
                    TextInput.active_input = None
                if self.callback:
                    self.callback(self.get_value())
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if self.numeric_only:
                    if event.unicode.isdigit() or event.unicode in [".", "-"]:
                        if event.unicode == "." and "." in self.text:
                            return True
                        if event.unicode == "-" and len(self.text) > 0:
                            return True
                        self.text += event.unicode
                else:
                    self.text += event.unicode
            return True
        return False

    def draw(self, screen: pygame.Surface):
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(screen, self.color_bg, self.rect, border_radius=4)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=4)

        text_surface = self.font.render(self.text, True, self.color_text)
        text_x = self.rect.x + 5
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2

        max_width = self.rect.width - 10
        if text_surface.get_width() > max_width:
            clip_rect = pygame.Rect(
                text_surface.get_width() - max_width,
                0,
                max_width,
                text_surface.get_height(),
            )
            screen.blit(text_surface, (text_x, text_y), clip_rect)
        else:
            screen.blit(text_surface, (text_x, text_y))

        if self.active:
            current_time = time.time()
            if current_time - self.last_blink_time > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.last_blink_time = current_time
            if self.cursor_visible:
                cursor_x = text_x + min(text_surface.get_width(), max_width) + 2
                pygame.draw.line(
                    screen,
                    self.color_text,
                    (cursor_x, text_y + 2),
                    (cursor_x, text_y + text_surface.get_height() - 2),
                    2,
                )


class SpinBox(Widget):
    """A numeric input with increment/decrement arrows."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        initial_val: int,
        min_val: int,
        max_val: int,
        step: int = 1,
        label: str = "",
        callback=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val, self.max_val, self.step = min_val, max_val, step
        self.callback = callback

        btn_width = 25
        text_width = width - (btn_width * 2) - 10
        self.text_input = TextInput(
            x,
            y,
            text_width,
            height,
            initial_text=str(initial_val),
            numeric_only=True,
            callback=self._on_text_change,
        )
        self.btn_dec = Button(
            x + text_width + 5,
            y,
            btn_width,
            height,
            "-",
            callback=self._decrement,
            font_size=20,
            border_width=1,
        )
        self.btn_inc = Button(
            x + text_width + btn_width + 10,
            y,
            btn_width,
            height,
            "+",
            callback=self._increment,
            font_size=20,
            border_width=1,
        )

    def shift_y(self, dy: int):
        self.rect.y += dy
        self.text_input.shift_y(dy)
        self.btn_dec.shift_y(dy)
        self.btn_inc.shift_y(dy)

    def _on_text_change(self, val):
        try:
            val = max(self.min_val, min(self.max_val, int(float(val))))
        except ValueError:
            val = self.min_val
        self.text_input.set_value(val)
        if self.callback:
            self.callback(val)

    def _decrement(self):
        self._on_text_change(int(self.text_input.get_value()) - self.step)

    def _increment(self):
        self._on_text_change(int(self.text_input.get_value()) + self.step)

    def handle_event(self, event: pygame.event.Event) -> bool:
        handled = self.text_input.handle_event(event)
        handled = self.btn_dec.handle_event(event) or handled
        handled = self.btn_inc.handle_event(event) or handled
        return handled

    def draw(self, screen: pygame.Surface):
        self.text_input.draw(screen)
        self.btn_dec.draw(screen)
        self.btn_inc.draw(screen)


class SliderWithText(Widget):
    """A composite widget linking a Slider and a TextInput."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        min_val: float,
        max_val: float,
        initial_val: float,
        label: str = "",
        callback=None,
    ):
        self.rect = pygame.Rect(x, y, width, 40)
        self.callback = callback

        text_width = 60
        slider_width = width - text_width - 10
        self.slider = Slider(
            x,
            y + 20,
            slider_width,
            min_val,
            max_val,
            initial_val,
            label="",
            callback=self._on_slider_change,
        )
        self.text_input = TextInput(
            x + slider_width + 10,
            y + 10,
            text_width,
            30,
            initial_text=f"{initial_val:.2f}",
            numeric_only=True,
            callback=self._on_text_change,
        )
        self.label, self.font = label, pygame.font.SysFont("consolas", 14)

    def shift_y(self, dy: int):
        self.rect.y += dy
        self.slider.shift_y(dy)
        self.text_input.shift_y(dy)

    def _on_slider_change(self, val: float):
        self.text_input.set_value(val)
        if self.callback:
            self.callback(val)

    def _on_text_change(self, val):
        try:
            val = max(self.slider.min_val, min(self.slider.max_val, float(val)))
        except ValueError:
            val = self.slider.min_val
        self.text_input.set_value(val)
        self.slider.set_value(val)
        if self.callback:
            self.callback(val)

    def handle_event(self, event: pygame.event.Event) -> bool:
        handled = self.slider.handle_event(event)
        handled = self.text_input.handle_event(event) or handled
        return handled

    def draw(self, screen: pygame.Surface):
        if self.label:
            text_surface = self.font.render(self.label, True, (200, 200, 200))
            screen.blit(text_surface, (self.rect.x, self.rect.y))
        self.slider.draw(screen)
        self.text_input.draw(screen)


class ScrollArea(Widget):
    """A masked container that safely offsets all internal elements using their native shift_y method."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.widgets = []
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        self.border_color = (60, 60, 70)

    def add_widget(self, widget):
        self.widgets.append(widget)
        self._recalculate_max_scroll()

    def _recalculate_max_scroll(self):
        if not self.widgets:
            self.max_scroll = 0
            return
        bottom_y = max(w.rect.bottom for w in self.widgets)
        content_height = bottom_y - self.rect.top
        self.max_scroll = max(0, content_height - self.rect.height + 20)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y -= event.y * self.scroll_speed
                self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
                return True

        is_mouse_event = event.type in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        )
        if is_mouse_event and hasattr(event, "pos"):
            if not self.rect.collidepoint(event.pos):
                return False

        handled = False

        # Shift down to event coordinates
        for w in self.widgets:
            w.shift_y(-self.scroll_y)

        for w in self.widgets:
            if w.handle_event(event):
                handled = True

        # Must always shift back
        for w in self.widgets:
            w.shift_y(self.scroll_y)

        return handled

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (25, 25, 30), self.rect)
        pygame.draw.line(
            screen, self.border_color, self.rect.topleft, self.rect.topright, 2
        )

        screen.set_clip(self.rect)

        for w in self.widgets:
            w.shift_y(-self.scroll_y)
            if w.rect.bottom > self.rect.top and w.rect.top < self.rect.bottom:
                w.draw(screen)
            w.shift_y(self.scroll_y)

        screen.set_clip(None)

        if self.max_scroll > 0:
            bar_rect = pygame.Rect(
                self.rect.right - 8, self.rect.y, 6, self.rect.height
            )
            pygame.draw.rect(screen, (40, 40, 45), bar_rect, border_radius=3)
            view_ratio = self.rect.height / (self.rect.height + self.max_scroll)
            handle_height = max(20, int(self.rect.height * view_ratio))
            scroll_ratio = self.scroll_y / self.max_scroll
            handle_y = self.rect.y + (self.rect.height - handle_height) * scroll_ratio
            handle_rect = pygame.Rect(self.rect.right - 8, handle_y, 6, handle_height)
            pygame.draw.rect(screen, (100, 150, 200), handle_rect, border_radius=3)
