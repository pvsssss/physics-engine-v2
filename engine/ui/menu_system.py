"""
Menu System for Physics Engine

Manages different screens:
- Main Menu: Title screen with navigation
- Scene Selection: Grid of available scenes
- Simulation: Running physics with UI controls
"""

import pygame
import sys
from enum import Enum, auto
from typing import Optional

from engine.ui.ui_framework import Button, Panel, SceneCard, Text, Slider
from engine.ui.scene_thumbnails import SCENE_INFO


class MenuState(Enum):
    """Different screen states."""

    MAIN_MENU = auto()
    SCENE_SELECT = auto()
    SIMULATION = auto()


class MenuSystem:
    """
    Manages menu navigation and rendering.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN_MENU
        self.selected_scene = None

        # Create all screens
        self._create_main_menu()
        self._create_scene_select()

    def _create_main_menu(self):
        """Create main menu screen elements."""
        # Main panel
        panel_width = 1536
        panel_height = 864
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        self.main_panel = Panel(panel_x, panel_y, panel_width, panel_height)

        # Buttons
        button_width = 400
        button_height = 80
        button_x = self.screen_width // 2 - button_width // 2

        self.main_buttons = []

        # Scenes button
        scenes_btn = Button(
            button_x,
            self.screen_height // 2 + 20,
            button_width,
            button_height,
            "SCENES",
            callback=lambda: self.go_to_scene_select(),
            font_size=36,
        )
        self.main_buttons.append(scenes_btn)

        # Quit button
        quit_btn = Button(
            button_x,
            self.screen_height // 2 + 140,
            button_width,
            button_height,
            "QUIT",
            callback=lambda: sys.exit(0),
            font_size=36,
        )
        self.main_buttons.append(quit_btn)

    def _create_scene_select(self):
        """Create scene selection screen elements."""
        # Main panel
        panel_width = 1536
        panel_height = 864
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        self.scene_panel = Panel(panel_x, panel_y, panel_width, panel_height)

        # Scene cards in 2x2 grid
        self.scene_cards = []

        card_width = 340
        card_height = 220
        spacing_x = 60
        spacing_y = 60

        start_x = panel_x + (panel_width - 2 * card_width - spacing_x) // 2
        start_y = panel_y + 80

        for i, scene_info in enumerate(SCENE_INFO):
            row = i // 2
            col = i % 2

            x = start_x + col * (card_width + spacing_x)
            y = start_y + row * (card_height + spacing_y)

            # Generate thumbnail
            thumbnail = scene_info["thumbnail_func"](200, 120)

            card = SceneCard(
                x,
                y,
                card_width,
                card_height,
                scene_info["name"],
                scene_info["description"],
                thumbnail=thumbnail,
                callback=lambda idx=i: self.select_scene(idx),
            )
            self.scene_cards.append(card)

        # Back button
        self.back_button = Button(
            20,
            self.screen_height - 80,
            120,
            60,
            "BACK",
            callback=lambda: self.go_to_main_menu(),
            font_size=24,
        )

    def go_to_main_menu(self):
        """Transition to main menu."""
        self.state = MenuState.MAIN_MENU
        self.selected_scene = None

    def go_to_scene_select(self):
        """Transition to scene selection."""
        self.state = MenuState.SCENE_SELECT

    def select_scene(self, scene_index: int):
        """Select a scene and go to simulation."""
        self.selected_scene = scene_index
        self.state = MenuState.SIMULATION

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events for current screen.
        Returns True if event was handled.
        """
        if self.state == MenuState.MAIN_MENU:
            for button in self.main_buttons:
                if button.handle_event(event):
                    return True

        elif self.state == MenuState.SCENE_SELECT:
            for card in self.scene_cards:
                if card.handle_event(event):
                    return True
            if self.back_button.handle_event(event):
                return True

        return False

    def draw(self, screen: pygame.Surface):
        """Draw current screen."""
        if self.state == MenuState.MAIN_MENU:
            self._draw_main_menu(screen)
        elif self.state == MenuState.SCENE_SELECT:
            self._draw_scene_select(screen)

    def _draw_main_menu(self, screen: pygame.Surface):
        """Draw main menu screen."""
        # Background
        screen.fill((20, 25, 30))

        # Main panel
        self.main_panel.draw(screen)

        # Title
        Text.draw_title(
            screen,
            "Physics Engine",
            self.screen_height // 2 - 180,
            self.screen_width,
            font_size=86,
        )

        # Buttons
        for button in self.main_buttons:
            button.draw(screen)

    def _draw_scene_select(self, screen: pygame.Surface):
        """Draw scene selection screen."""
        # Background
        screen.fill((20, 25, 30))

        # Title
        Text.draw_title(screen, "SCENES", 60, self.screen_width, font_size=48)

        # Main panel
        self.scene_panel.draw(screen)

        # Scene cards
        for card in self.scene_cards:
            card.draw(screen)

        # Back button
        self.back_button.draw(screen)


class SimulationUI:
    """
    UI overlay for simulation screen (right panel with controls).
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        scene_index: int,
        on_back: callable,
        on_reset: callable,
        on_pause: callable,
        on_step: callable,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scene_info = SCENE_INFO[scene_index]
        self.toggles = {}

        # Layout: simulation on left, controls on right
        self.panel_width = 300
        self.sim_width = 1236

        # Control panel
        self.control_panel = Panel(
            self.sim_width - 2, 0, self.panel_width, screen_height
        )

        # Control buttons
        self.buttons = []

        btn_x = self.sim_width + 25
        btn_width = self.panel_width - 50
        btn_height = 45

        # Scene name at top
        self.title_y = 25

        # Reset button
        reset_btn = Button(
            btn_x,
            80,
            btn_width,
            btn_height,
            "Reset (R)",
            callback=on_reset,
            font_size=20,
        )
        self.buttons.append(reset_btn)

        # Pause button
        pause_btn = Button(
            btn_x,
            140,
            btn_width,
            btn_height,
            "Pause (SPACE)",
            callback=on_pause,
            font_size=20,
        )
        self.buttons.append(pause_btn)

        # Step button
        step_btn = Button(
            btn_x,
            200,
            btn_width,
            btn_height,
            "Step (S)",
            callback=on_step,
            font_size=20,
        )
        self.buttons.append(step_btn)

        y_offset = 280

        # Add scene-specific controls based on scene type
        scene_name = self.scene_info["name"]

        if "Projectile" in scene_name:
            self._add_projectile_controls(btn_x, btn_width, y_offset)
        elif "Buoyancy" in scene_name:
            self._add_buoyancy_controls(btn_x, btn_width, y_offset)
        elif "Rope" in scene_name or "Circle" in scene_name:
            self._add_container_controls(btn_x, btn_width, y_offset)

        # Back button at bottom
        back_btn = Button(
            btn_x,
            screen_height - 70,
            btn_width,
            50,
            "Back to Menu",
            callback=on_back,
            font_size=22,
        )
        self.buttons.append(back_btn)

        # Store toggle states

    def _add_projectile_controls(self, x: int, width: int, y_start: int):
        """Add projectile-specific controls."""
        y = y_start

        # Section label
        self.projectile_label_y = y - 20

        # Toggle trajectory
        btn = Button(
            x,
            y,
            width,
            38,
            "Trajectory (T)",
            callback=lambda: self.toggle("trajectory"),
            font_size=18,
        )
        self.buttons.append(btn)
        self.toggles["trajectory"] = True
        y += 48

        # Toggle coordinates
        btn = Button(
            x,
            y,
            width,
            38,
            "Coords (O)",
            callback=lambda: self.toggle("coordinates"),
            font_size=18,
        )
        self.buttons.append(btn)
        self.toggles["coordinates"] = True
        y += 48

        # Toggle scale
        btn = Button(
            x,
            y,
            width,
            38,
            "Scale (L)",
            callback=lambda: self.toggle("scale"),
            font_size=18,
        )
        self.buttons.append(btn)
        self.toggles["scale"] = True

    def _add_buoyancy_controls(self, x: int, width: int, y_start: int):
        """Add buoyancy-specific controls."""
        y = y_start

        self.buoyancy_label_y = y - 20

        # Toggle water
        btn = Button(
            x,
            y,
            width,
            38,
            "Water (W)",
            callback=lambda: self.toggle("water"),
            font_size=18,
        )
        self.buttons.append(btn)
        self.toggles["water"] = True
        y += 48

        # Toggle scale
        btn = Button(
            x,
            y,
            width,
            38,
            "Scale (L)",
            callback=lambda: self.toggle("scale"),
            font_size=18,
        )
        self.buttons.append(btn)
        self.toggles["scale"] = True

    def _add_container_controls(self, x: int, width: int, y_start: int):
        """Add container scene controls."""
        y = y_start

        # Toggle constraints
        btn = Button(
            x,
            y,
            width,
            38,
            "Constraints (C)",
            callback=lambda: self.toggle("constraints"),
            font_size=18,
        )
        self.buttons.append(btn)
        self.toggles["constraints"] = True

    def toggle(self, name: str):
        """Toggle a UI state."""
        if name in self.toggles:
            self.toggles[name] = not self.toggles[name]

    def get_toggle(self, name: str) -> bool:
        """Get state of a toggle."""
        return self.toggles.get(name, False)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """Draw the UI panel."""
        # Control panel
        self.control_panel.draw(screen)

        # Scene name
        Text.draw(
            screen,
            self.scene_info["name"],
            self.sim_width + self.panel_width // 2,
            self.title_y,
            font_size=22,
            bold=True,
            center=True,
        )

        # Section label if needed
        scene_name = self.scene_info["name"]
        if "Projectile" in scene_name and hasattr(self, "projectile_label_y"):
            Text.draw(
                screen,
                "Display:",
                self.sim_width + 40,
                self.projectile_label_y,
                font_size=16,
                color=(150, 150, 150),
                bold=True,
            )
        elif "Buoyancy" in scene_name and hasattr(self, "buoyancy_label_y"):
            Text.draw(
                screen,
                "Display:",
                self.sim_width + 40,
                self.buoyancy_label_y,
                font_size=16,
                color=(150, 150, 150),
                bold=True,
            )

        # Buttons
        for button in self.buttons:
            button.draw(screen)
