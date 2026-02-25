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

from engine.ui.ui_framework import (
    Widget,
    Button,
    Panel,
    SceneCard,
    Text,
    Slider,
    TextInput,
    SpinBox,
    SliderWithText,
    ScrollArea,
)
from engine.ui.scene_thumbnails import SCENE_INFO

from engine.core.config_manager import config_manager
from engine.physics.forces import (
    Gravity,
    WindForce,
    LinearDrag,
    WaterDragForce,
    BuoyancyForce,
)
from engine.math.vec import Vec2


class MenuState(Enum):
    MAIN_MENU = auto()
    SCENE_SELECT = auto()
    SIMULATION = auto()


class LabelWidget(Widget):
    def __init__(self, x, y, text, color=(200, 200, 200), font_size=16):
        self.rect = pygame.Rect(x, y, 200, 20)
        self.text = text
        self.color = color
        try:
            self.font = pygame.font.Font("assets/LilitaOne-Regular.ttf", font_size)
        except:
            self.font = pygame.font.SysFont("impact", font_size)

    def handle_event(self, event):
        return False

    def draw(self, screen):
        screen.blit(
            self.font.render(self.text, True, self.color), (self.rect.x, self.rect.y)
        )


class RowWidget(Widget):
    def __init__(self, x, y, width, height, widgets):
        self.rect = pygame.Rect(x, y, width, height)
        self.widgets = widgets

    def shift_y(self, dy: int):
        self.rect.y += dy
        for w in self.widgets:
            w.shift_y(dy)

    def handle_event(self, event):
        handled = False
        for w in self.widgets:
            if w.handle_event(event):
                handled = True
        return handled

    def draw(self, screen):
        for w in self.widgets:
            w.draw(screen)


class MenuSystem:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN_MENU
        self.selected_scene = None

        self._create_main_menu()
        self._create_scene_select()

    def _create_main_menu(self):
        panel_width, panel_height = 1536, 864
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        self.main_panel = Panel(panel_x, panel_y, panel_width, panel_height)
        button_width, button_height = 400, 80
        button_x = self.screen_width // 2 - button_width // 2

        self.btn_start = Button(
            button_x,
            self.screen_height // 2 - 50,
            button_width,
            button_height,
            "Start Simulation",
            callback=self.go_to_scene_select,
        )
        self.btn_quit = Button(
            button_x,
            self.screen_height // 2 + 50,
            button_width,
            button_height,
            "Quit",
            callback=self.quit_app,
            bg_color=(150, 50, 50),
            hover_color=(200, 70, 70),
        )
        self.main_menu_buttons = [self.btn_start, self.btn_quit]

    def _create_scene_select(self):
        panel_width = 1536
        panel_height = 864
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        self.scene_panel = Panel(panel_x, panel_y, panel_width, panel_height)
        self.scene_cards = []

        card_width, card_height = 460, 280
        spacing_x, spacing_y = 90, 70
        cols = 2

        total_width = (cols * card_width) + ((cols - 1) * spacing_x)
        start_x = (self.screen_width - total_width) // 2
        total_height = (2 * card_height) + spacing_y
        start_y = (self.screen_height - total_height) // 2 + 50

        for i, scene_info in enumerate(SCENE_INFO):
            row = i // cols
            col = i % cols

            x = start_x + col * (card_width + spacing_x)
            y = start_y + row * (card_height + spacing_y)

            thumbnail = scene_info.get("thumbnail_func", lambda w, h: None)(380, 220)

            card = SceneCard(
                x,
                y,
                card_width,
                card_height,
                scene_info["name"],
                scene_info["description"],
                thumbnail=thumbnail,
                callback=lambda idx=i: self.start_scene(idx),
            )
            self.scene_cards.append(card)

        self.btn_back = Button(
            20,
            self.screen_height - 80,
            120,
            60,
            "BACK",
            callback=self.go_to_main_menu,
            font_size=24,
        )

    def go_to_main_menu(self):
        self.state = MenuState.MAIN_MENU

    def go_to_scene_select(self):
        self.state = MenuState.SCENE_SELECT

    def start_scene(self, scene_index: int):
        self.selected_scene = scene_index
        self.state = MenuState.SIMULATION

    def quit_app(self):
        pygame.quit()
        sys.exit()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.state == MenuState.MAIN_MENU:
            for btn in self.main_menu_buttons:
                if btn.handle_event(event):
                    return True
        elif self.state == MenuState.SCENE_SELECT:
            if self.btn_back.handle_event(event):
                return True
            for card in self.scene_cards:
                if card.handle_event(event):
                    return True
        return False

    def draw(self, screen: pygame.Surface):
        if self.state == MenuState.MAIN_MENU:
            self.main_panel.draw(screen)
            Text.draw_title(screen, "2D PHYSICS ENGINE", 200, self.screen_width)
            for btn in self.main_menu_buttons:
                btn.draw(screen)
        elif self.state == MenuState.SCENE_SELECT:
            self.scene_panel.draw(screen)
            Text.draw_title(
                screen, "SELECT SCENE", 100, self.screen_width, font_size=48
            )
            for card in self.scene_cards:
                card.draw(screen)
            self.btn_back.draw(screen)


class SimulationUI:

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        scene_index: int,
        on_back,
        on_reset,
        on_pause,
        on_step,
    ):
        self.panel_width = 300
        self.sim_width = screen_width - self.panel_width
        self.control_panel = Panel(self.sim_width, 0, self.panel_width, screen_height)

        self.scene_info = SCENE_INFO[scene_index]
        self.scene_name_key = self.scene_info["scene_module"]
        self.on_reset_callback = on_reset

        self.buttons = []
        self.toggles = {}

        self.psystem = None
        self.interaction = None
        self.is_paused = False
        self.last_selected_particle = None

        # Build controls and calculate dynamic Y spacing for the Reset button
        self._build_top_controls(on_back, on_reset, on_pause, on_step)

        if "Projectile" in self.scene_info["name"]:
            current_y = 365
        elif "Buoyancy" in self.scene_info["name"]:
            current_y = 315
        else:
            current_y = 265

        self.btn_reset_config = Button(
            self.sim_width + 30,
            current_y,
            240,
            40,
            "Reset Config",
            callback=self._reset_config,
            font_size=20,
            bg_color=(150, 50, 50),
            hover_color=(200, 70, 70),
        )
        self.buttons.append(self.btn_reset_config)

        current_y += 50
        self.scroll_area = ScrollArea(
            self.sim_width + 10,
            current_y,
            self.panel_width - 20,
            screen_height - current_y - 20,
        )

        self.global_widgets = []
        self.particle_widgets = []

        self._build_global_ui()
        self._build_particle_ui()
        self._layout_scroll_area()

    def _build_top_controls(self, on_back, on_reset, on_pause, on_step):
        btn_w, btn_h = 120, 40
        start_x = self.sim_width + (self.panel_width - (btn_w * 2 + 10)) // 2

        self.buttons.append(
            Button(start_x, 60, btn_w, btn_h, "Back", callback=on_back, font_size=20)
        )
        self.buttons.append(
            Button(
                start_x + btn_w + 10,
                60,
                btn_w,
                btn_h,
                "Reset",
                callback=on_reset,
                font_size=20,
            )
        )
        self.buttons.append(
            Button(
                start_x,
                110,
                btn_w,
                btn_h,
                "Play/Pause",
                callback=on_pause,
                font_size=20,
            )
        )
        self.buttons.append(
            Button(
                start_x + btn_w + 10,
                110,
                btn_w,
                btn_h,
                "Step",
                callback=on_step,
                font_size=20,
            )
        )

        scene_name = self.scene_info["name"]
        toggle_x = self.sim_width + 30
        toggle_w = 240
        toggle_h = 40
        toggle_y = 165

        # 1. Global Velocities Toggle (Applies to all scenes)
        self.toggles["velocities"] = False
        self.buttons.append(
            Button(
                toggle_x,
                toggle_y,
                toggle_w,
                toggle_h,
                "Velocities (V)",
                callback=lambda: self.toggle("velocities"),
                font_size=18,
            )
        )
        toggle_y += 50

        # 2. Scene-Specific Toggles
        if "Rope" in scene_name or "Circle" in scene_name:
            self.toggles["constraints"] = True
            self.buttons.append(
                Button(
                    toggle_x,
                    toggle_y,
                    toggle_w,
                    toggle_h,
                    "Constraints (C)",
                    callback=lambda: self.toggle("constraints"),
                    font_size=18,
                )
            )
            toggle_y += 50

        if "Projectile" in scene_name:
            self.toggles["trajectory"] = True
            self.toggles["coordinates"] = False
            self.toggles["scale"] = True
            self.buttons.append(
                Button(
                    toggle_x,
                    toggle_y,
                    toggle_w,
                    toggle_h,
                    "Trajectory (T)",
                    callback=lambda: self.toggle("trajectory"),
                    font_size=18,
                )
            )
            self.buttons.append(
                Button(
                    toggle_x,
                    toggle_y + 50,
                    toggle_w,
                    toggle_h,
                    "Coords (O)",
                    callback=lambda: self.toggle("coordinates"),
                    font_size=18,
                )
            )
            self.buttons.append(
                Button(
                    toggle_x,
                    toggle_y + 100,
                    toggle_w,
                    toggle_h,
                    "Scale (L)",
                    callback=lambda: self.toggle("scale"),
                    font_size=18,
                )
            )
            toggle_y += 125

        if "Buoyancy" in scene_name:
            self.toggles["water"] = True
            self.toggles["scale"] = True
            self.buttons.append(
                Button(
                    toggle_x,
                    toggle_y,
                    toggle_w,
                    toggle_h,
                    "Water (Q)",
                    callback=lambda: self.toggle("water"),
                    font_size=18,
                )
            )
            self.buttons.append(
                Button(
                    toggle_x,
                    toggle_y + 50,
                    toggle_w,
                    toggle_h,
                    "Scale (L)",
                    callback=lambda: self.toggle("scale"),
                    font_size=18,
                )
            )
            toggle_y += 100

        self.final_toggle_y = (
            toggle_y
            + 50  # Save this so the Reset Config button anchors perfectly below
        )

    def _build_global_ui(self):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        x = self.sim_width + 20

        self.global_widgets.append(
            LabelWidget(x, 0, "GLOBAL SETTINGS", color=(255, 200, 100), font_size=20)
        )

        if "gravity" in cfg:
            self.global_widgets.append(
                LabelWidget(x, 0, "Gravity (X, Y):", font_size=14)
            )
            # Save as self.grav_x_input so we can update it later
            self.grav_x_input = TextInput(
                x,
                0,
                120,
                30,
                initial_text=str(cfg["gravity"].x),
                numeric_only=True,
                callback=self._on_grav_x,
            )
            self.grav_y_input = TextInput(
                x + 130,
                0,
                120,
                30,
                initial_text=str(cfg["gravity"].y),
                numeric_only=True,
                callback=self._on_grav_y,
            )
            self.global_widgets.append(
                RowWidget(x, 0, 260, 30, [self.grav_x_input, self.grav_y_input])
            )

        if "wind_force" in cfg:
            self.global_widgets.append(
                LabelWidget(x, 0, "Wind Force (X, Y):", font_size=14)
            )
            self.wind_x_input = TextInput(
                x,
                0,
                120,
                30,
                initial_text=str(cfg["wind_force"].x),
                numeric_only=True,
                callback=self._on_wind_x,
            )
            self.wind_y_input = TextInput(
                x + 130,
                0,
                120,
                30,
                initial_text=str(cfg["wind_force"].y),
                numeric_only=True,
                callback=self._on_wind_y,
            )
            self.global_widgets.append(
                RowWidget(x, 0, 260, 30, [self.wind_x_input, self.wind_y_input])
            )

        if "air_drag" in cfg:
            self.global_widgets.append(LabelWidget(x, 0, "Air Drag:", font_size=14))
            self.air_drag_input = TextInput(
                x,
                0,
                250,
                30,
                initial_text=str(cfg["air_drag"]),
                numeric_only=True,
                callback=self._on_air_drag,
            )
            self.global_widgets.append(self.air_drag_input)

        if "water_drag" in cfg:
            self.global_widgets.append(LabelWidget(x, 0, "Water Drag:", font_size=14))
            self.water_drag_input = TextInput(
                x,
                0,
                250,
                30,
                initial_text=str(cfg["water_drag"]),
                numeric_only=True,
                callback=self._on_water_drag,
            )
            self.global_widgets.append(self.water_drag_input)

        if "fluid_density" in cfg:
            self.global_widgets.append(
                LabelWidget(x, 0, "Fluid Density:", font_size=14)
            )
            self.fluid_density_input = TextInput(
                x,
                0,
                250,
                30,
                initial_text=str(cfg["fluid_density"]),
                numeric_only=True,
                callback=self._on_fluid_density,
            )
            self.global_widgets.append(self.fluid_density_input)

        if "particle_count" in cfg:
            self.global_widgets.append(
                LabelWidget(x, 0, "Particle Count:", font_size=14)
            )
            self.global_widgets.append(
                LabelWidget(
                    x, 0, "(Applies on Reset)", color=(150, 150, 150), font_size=12
                )
            )
            self.particle_count_input = SpinBox(
                x,
                0,
                250,
                30,
                initial_val=cfg["particle_count"],
                min_val=1,
                max_val=100,
                label="",
                callback=self._on_particle_count,
            )
            self.global_widgets.append(self.particle_count_input)

    def _build_particle_ui(self):
        x = self.sim_width + 20
        self.particle_widgets.append(
            LabelWidget(x, 0, "SELECTED PARTICLE", color=(100, 255, 100), font_size=20)
        )

        self.particle_widgets.append(
            LabelWidget(x, 0, "Position (X, Y):", font_size=14)
        )
        self.pos_x_input = TextInput(
            x, 0, 120, 30, numeric_only=True, callback=self._on_pos_x
        )
        self.pos_y_input = TextInput(
            x + 130, 0, 120, 30, numeric_only=True, callback=self._on_pos_y
        )
        self.particle_widgets.append(
            RowWidget(x, 0, 260, 30, [self.pos_x_input, self.pos_y_input])
        )

        self.particle_widgets.append(
            LabelWidget(x, 0, "Velocity (X, Y):", font_size=14)
        )
        self.vel_x_input = TextInput(
            x, 0, 120, 30, numeric_only=True, callback=self._on_vel_x
        )
        self.vel_y_input = TextInput(
            x + 130, 0, 120, 30, numeric_only=True, callback=self._on_vel_y
        )
        self.particle_widgets.append(
            RowWidget(x, 0, 260, 30, [self.vel_x_input, self.vel_y_input])
        )

        self.particle_widgets.append(LabelWidget(x, 0, "Mass:", font_size=14))
        self.mass_input = TextInput(
            x, 0, 250, 30, numeric_only=True, callback=self._on_mass
        )
        self.particle_widgets.append(self.mass_input)

        self.particle_widgets.append(LabelWidget(x, 0, "Radius:", font_size=14))
        self.radius_input = TextInput(
            x, 0, 250, 30, numeric_only=True, callback=self._on_radius
        )
        self.particle_widgets.append(self.radius_input)

        self.fric_slider = SliderWithText(
            x, 0, 250, 0.0, 1.0, 0.3, label="Friction", callback=self._on_fric
        )
        self.particle_widgets.append(self.fric_slider)

        self.rest_slider = SliderWithText(
            x, 0, 250, 0.0, 1.0, 0.4, label="Restitution", callback=self._on_rest
        )
        self.particle_widgets.append(self.rest_slider)

        self.remove_btn = Button(
            x,
            0,
            250,
            35,
            "Remove Selected",
            callback=self._on_remove,
            bg_color=(200, 50, 50),
            font_size=16,
        )
        self.particle_widgets.append(self.remove_btn)

    def _layout_scroll_area(self):
        """Forces every component to perfectly adopt the new base Y coordinate before placing it."""
        cy = self.scroll_area.rect.y + 10
        self.scroll_area.widgets.clear()

        for w in self.global_widgets:
            w.set_y(cy)
            cy += w.rect.height + 15
            self.scroll_area.add_widget(w)

        if self.last_selected_particle:
            cy += 15
            for w in self.particle_widgets:
                w.set_y(cy)
                cy += w.rect.height + 15
                self.scroll_area.add_widget(w)

        self.scroll_area._recalculate_max_scroll()

    def update(self, psystem, interaction, is_paused):
        self.psystem = psystem
        self.interaction = interaction
        self.is_paused = is_paused

        current_particle = interaction.selected_particle if interaction else None

        if current_particle != self.last_selected_particle:
            self.last_selected_particle = current_particle
            self._layout_scroll_area()

        if current_particle and current_particle.alive:
            if not self.pos_x_input.active:
                self.pos_x_input.set_value(current_particle.position.x)
            if not self.pos_y_input.active:
                self.pos_y_input.set_value(current_particle.position.y)
            if not self.vel_x_input.active:
                self.vel_x_input.set_value(current_particle.velocity.x)
            if not self.vel_y_input.active:
                self.vel_y_input.set_value(current_particle.velocity.y)

            if not self.mass_input.active:
                self.mass_input.set_value(current_particle.mass)
            if not self.radius_input.active:
                self.radius_input.set_value(current_particle.radius)

            if (
                not self.fric_slider.slider.dragging
                and not self.fric_slider.text_input.active
            ):
                self.fric_slider.slider.set_value(current_particle.friction)
                self.fric_slider.text_input.set_value(current_particle.friction)

            if (
                not self.rest_slider.slider.dragging
                and not self.rest_slider.text_input.active
            ):
                self.rest_slider.slider.set_value(current_particle.restitution)
                self.rest_slider.text_input.set_value(current_particle.restitution)

            if self.is_paused and interaction:
                if interaction.dragging_position:
                    self._update_particle_config(
                        "position", current_particle.position.x, "x"
                    )
                    self._update_particle_config(
                        "position", current_particle.position.y, "y"
                    )
                if interaction.dragging_velocity:
                    self._update_particle_config(
                        "velocity", current_particle.velocity.x, "x"
                    )
                    self._update_particle_config(
                        "velocity", current_particle.velocity.y, "y"
                    )

            self.remove_btn.enabled = self.is_paused

        elif current_particle and not current_particle.alive:
            if interaction:
                interaction.selected_particle = None
            self.last_selected_particle = None
            self._layout_scroll_area()

    def _update_particle_config(self, prop: str, val: float, comp: str = None):
        cfg = config_manager.get_scene_config(self.scene_name_key)

        possible_keys = []
        if prop == "position":
            possible_keys = ["initial_position"]
        elif prop == "velocity":
            possible_keys = ["initial_velocity"]
        elif prop == "mass":
            possible_keys = ["particle_mass", "mass"]
        elif prop == "radius":
            possible_keys = ["particle_radius", "radius", "radius_min", "radius_max"]
        elif prop == "friction":
            possible_keys = ["friction", "particle_friction"]
        elif prop == "restitution":
            possible_keys = ["restitution", "particle_restitution"]

        for k in possible_keys:
            if k in cfg:
                if comp == "x":
                    cfg[k].x = float(val)
                elif comp == "y":
                    cfg[k].y = float(val)
                else:
                    cfg[k] = float(val)

    def toggle(self, name: str):
        if name in self.toggles:
            self.toggles[name] = not self.toggles[name]

    def _sync_global_ui(self):
        """Forces the global UI text boxes to pull their values from the active config memory."""
        cfg = config_manager.get_scene_config(self.scene_name_key)

        if hasattr(self, "grav_x_input"):
            self.grav_x_input.set_value(cfg["gravity"].x)
            self.grav_y_input.set_value(cfg["gravity"].y)

        if hasattr(self, "wind_x_input"):
            self.wind_x_input.set_value(cfg["wind_force"].x)
            self.wind_y_input.set_value(cfg["wind_force"].y)

        if hasattr(self, "air_drag_input"):
            self.air_drag_input.set_value(cfg["air_drag"])

        if hasattr(self, "water_drag_input"):
            self.water_drag_input.set_value(cfg["water_drag"])

        if hasattr(self, "fluid_density_input"):
            self.fluid_density_input.set_value(cfg["fluid_density"])

        if hasattr(self, "particle_count_input"):
            self.particle_count_input.text_input.set_value(cfg["particle_count"])

    def _reset_config(self):
        # 1. Wipe the memory back to the hardcoded python defaults
        config_manager.reset_scene_config(self.scene_name_key)

        # 2. Visually update all the text boxes to match the restored memory
        self._sync_global_ui()

        # 3. Actually reset the physics engine
        self.on_reset_callback()

    def _on_grav_x(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["gravity"].x = float(val)
        if self.psystem:
            for f in self.psystem.global_forces:
                if isinstance(f, Gravity):
                    f.g.x = float(val)

    def _on_grav_y(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["gravity"].y = float(val)
        if self.psystem:
            for f in self.psystem.global_forces:
                if isinstance(f, Gravity):
                    f.g.y = float(val)

    def _on_wind_x(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["wind_force"].x = float(val)
        if self.psystem:
            for f in self.psystem.global_forces:
                if isinstance(f, WindForce):
                    f.force.x = float(val)

    def _on_wind_y(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["wind_force"].y = float(val)
        if self.psystem:
            for f in self.psystem.global_forces:
                if isinstance(f, WindForce):
                    f.force.y = float(val)

    def _on_air_drag(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["air_drag"] = float(val)
        if self.psystem:
            for f in self.psystem.global_forces:
                if isinstance(f, LinearDrag):
                    f.k = float(val)

    def _on_water_drag(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["water_drag"] = float(val)
        if self.psystem:
            for f in self.psystem.global_forces:
                if isinstance(f, WaterDragForce):
                    f.drag_coefficient = float(val)

    def _on_fluid_density(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["fluid_density"] = float(val)
        if self.psystem:
            for f in self.psystem.global_forces:
                if isinstance(f, BuoyancyForce) or isinstance(f, WaterDragForce):
                    f.fluid_density = float(val)

    def _on_particle_count(self, val):
        cfg = config_manager.get_scene_config(self.scene_name_key)
        cfg["particle_count"] = int(val)

    def _on_pos_x(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.position.x = float(val)
        self._update_particle_config("position", val, "x")

    def _on_pos_y(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.position.y = float(val)
        self._update_particle_config("position", val, "y")

    def _on_vel_x(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.velocity.x = float(val)
        self._update_particle_config("velocity", val, "x")

    def _on_vel_y(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.velocity.y = float(val)
        self._update_particle_config("velocity", val, "y")

    def _on_mass(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.mass = float(val)
            self.last_selected_particle.inv_mass = (
                1.0 / float(val) if float(val) > 0 else 0.0
            )
        self._update_particle_config("mass", val)

    def _on_radius(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.radius = float(val)
        self._update_particle_config("radius", val)

    def _on_fric(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.friction = float(val)
        self._update_particle_config("friction", val)

    def _on_rest(self, val):
        if self.last_selected_particle:
            self.last_selected_particle.restitution = float(val)
        self._update_particle_config("restitution", val)

    def _on_remove(self):
        if self.last_selected_particle and self.is_paused:
            self.last_selected_particle.kill()
            cfg = config_manager.get_scene_config(self.scene_name_key)
            if "particle_count" in cfg and cfg["particle_count"] > 0:
                cfg["particle_count"] -= 1

    def get_toggle(self, name: str) -> bool:
        return self.toggles.get(name, False)

    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        if self.scroll_area.handle_event(event):
            return True
        return False

    def draw(self, screen: pygame.Surface):
        self.control_panel.draw(screen)
        Text.draw(
            screen,
            self.scene_info["name"],
            self.sim_width + self.panel_width // 2,
            20,
            font_size=24,
            bold=True,
            center=True,
        )
        for button in self.buttons:
            button.draw(screen)
        self.scroll_area.draw(screen)
