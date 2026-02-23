"""
Configuration Manager
Loads hardcoded defaults, stores active UI configurations in memory,
and provides reset functionality for scenes.
"""

from __future__ import annotations
from typing import Any, Dict

from engine.math.vec import Vec2
from engine.scenes import projectile_config, buoyancy_config


class ConfigManager:
    """Singleton manager holding the default and active states for all scenes."""

    def __init__(self):
        self.defaults: Dict[str, Dict[str, Any]] = {
            "projectile_scene": {
                "gravity": projectile_config.GRAVITY.copy(),
                "wind_force": projectile_config.WIND_FORCE.copy(),
                "initial_position": projectile_config.INITIAL_POSITION.copy(),
                "initial_velocity": projectile_config.INITIAL_VELOCITY.copy(),
                "particle_radius": projectile_config.PARTICLE_RADIUS,
                "particle_mass": projectile_config.PARTICLE_MASS,
                "restitution": projectile_config.RESTITUTION,
                "friction": projectile_config.FRICTION,
                "damping": projectile_config.DAMPING,
            },
            "buoyancy_scene": {
                "gravity": buoyancy_config.GRAVITY.copy(),
                "air_drag": buoyancy_config.AIR_DRAG_COEFFICIENT,
                "water_drag": buoyancy_config.WATER_DRAG_COEFFICIENT,
                "fluid_density": buoyancy_config.FLUID_DENSITY,
                "particle_count": buoyancy_config.PARTICLE_COUNT,
                "radius_min": buoyancy_config.PARTICLE_RADIUS_MIN,
                "radius_max": buoyancy_config.PARTICLE_RADIUS_MAX,
                "density_min": buoyancy_config.PARTICLE_DENSITY_MIN,
                "density_max": buoyancy_config.PARTICLE_DENSITY_MAX,
            },
            "circle_container_scene": {
                "gravity": Vec2(
                    0.0, -1200.0
                ),  # Fixed to negative Y (Bottom-Left coords)
                "particle_count": 10,
                "mass": 1.0,
                "radius": 15.0,
                "restitution": 0.7,
                "friction": 0.1,
                "damping": 0.05,
            },
            "rope_scene": {
                "gravity": Vec2(
                    0.0, -800.0
                ),  # Fixed to negative Y (Bottom-Left coords)
                "particle_count": 15,
            },
        }

        self.active: Dict[str, Dict[str, Any]] = self._deep_copy_dict(self.defaults)

    def _deep_copy_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_dict(value)
            elif isinstance(value, Vec2):
                result[key] = value.copy()
            else:
                result[key] = value
        return result

    def get_scene_config(self, scene_name: str) -> Dict[str, Any]:
        return self.active.get(scene_name, {})

    def update_global(self, scene_name: str, key: str, value: Any) -> None:
        if scene_name in self.active:
            if isinstance(self.active[scene_name].get(key), Vec2) and isinstance(
                value, Vec2
            ):
                self.active[scene_name][key].x = value.x
                self.active[scene_name][key].y = value.y
            else:
                self.active[scene_name][key] = value

    def reset_scene_config(self, scene_name: str) -> None:
        if scene_name in self.defaults:
            self.active[scene_name] = self._deep_copy_dict(self.defaults[scene_name])


config_manager = ConfigManager()
