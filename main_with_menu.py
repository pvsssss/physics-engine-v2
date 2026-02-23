"""
Physics Engine with Menu System
Main entry point with UI navigation.
"""

import pygame

from engine.physics.particle_system import ParticleSystem
from engine.core.simulation_controller import SimulationController
from engine.render.pygame_renderer import PygameRenderer
from engine.physics import solver
from engine.core.interaction import InteractionHandler  # Added Interaction Handler

# Import scenes
from engine.scenes import (
    rope_scene,
    circle_container_scene,
    projectile_scene,
    projectile_config,
    buoyancy_scene,
    buoyancy_config,
)

# Import UI system
from engine.ui.ui_framework import *
from engine.ui.menu_system import MenuSystem, SimulationUI, MenuState
from engine.ui.scene_thumbnails import SCENE_INFO


def main() -> None:
    pygame.init()

    # Screen setup
    monitor_info = pygame.display.Info()

    SCREEN_WIDTH = monitor_info.current_w
    SCREEN_HEIGHT = monitor_info.current_h
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
    )
    pygame.display.set_caption("Physics Engine")

    # Create menu system
    menu = MenuSystem(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Physics components (created when entering simulation)
    renderer = None
    controller = None
    psystem = None
    sim_ui = None
    interaction = None  # Added Interaction Handler state
    current_scene_module = None

    # Main loop
    clock = pygame.time.Clock()
    running = True

    # Physics timing
    FIXED_DT = 1.0 / 144.0
    accumulator = 0.0

    while running:
        frame_dt = clock.tick(144) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu.state == MenuState.SIMULATION:
                        menu.go_to_main_menu()
                    else:
                        running = False

                # Simulation controls (only in simulation mode)
                if menu.state == MenuState.SIMULATION and controller:
                    if event.key == pygame.K_SPACE:
                        controller.toggle_pause()
                    elif event.key == pygame.K_s:
                        controller.request_step()
                    elif event.key == pygame.K_r:
                        controller.request_reset()  # Normal reset (keeps custom config)
                    elif event.key == pygame.K_w:
                        if sim_ui:
                            sim_ui._reset_config()  # Hard reset (restores defaults)
                    elif event.key == pygame.K_c:
                        if renderer:
                            renderer.draw_constraints = not renderer.draw_constraints
                    elif event.key == pygame.K_t:
                        if sim_ui:
                            sim_ui.toggle("trajectory")
                    elif event.key == pygame.K_o:
                        if sim_ui:
                            sim_ui.toggle("coordinates")
                    elif event.key == pygame.K_l:
                        if sim_ui:
                            sim_ui.toggle("scale")
                    elif (
                        event.key == pygame.K_q
                    ):  # Shifted from 'w' to free up Reset Config
                        if sim_ui:
                            sim_ui.toggle("water")
            # Handle UI and Interaction events
            if menu.state != MenuState.SIMULATION:
                menu.handle_event(event)
            else:
                ui_handled = False
                if sim_ui:
                    ui_handled = sim_ui.handle_event(event)

                # If UI didn't consume the event, and we are PAUSED, let interaction handler run
                if not ui_handled and controller and controller.paused and interaction:
                    # 1236 is the simulation area width
                    interaction.handle_event(event, renderer.camera, psystem, 1236)

        # State transitions - setup simulation when entering
        if menu.state == MenuState.SIMULATION and psystem is None:
            # Initialize physics components
            renderer = PygameRenderer()
            controller = SimulationController()
            psystem = ParticleSystem()
            interaction = InteractionHandler()  # Initialize Interaction Handler

            # Get scene module
            scene_info = SCENE_INFO[menu.selected_scene]
            scene_name = scene_info["scene_module"]

            if scene_name == "rope_scene":
                current_scene_module = rope_scene
            elif scene_name == "circle_container_scene":
                current_scene_module = circle_container_scene
            elif scene_name == "projectile_scene":
                current_scene_module = projectile_scene
            elif scene_name == "buoyancy_scene":
                current_scene_module = buoyancy_scene

            # Build scene
            current_scene_module.build(psystem)
            if scene_name == "buoyancy_scene":
                solver.PERCENT = 4
                solver.MAX_CORRECTION_PER_ITERATION = 20000
            else:
                solver.PERCENT = 0.2
                solver.MAX_CORRECTION_PER_ITERATION = 2

            # Configure renderer for scene
            if scene_name == "projectile_scene":
                renderer.draw_trajectories = True
                renderer.draw_coordinates = True
                renderer.draw_scale = True
                renderer.use_bottom_left_origin = True
            elif scene_name == "buoyancy_scene":
                renderer.draw_water = True
                renderer.draw_scale = True
                renderer.use_bottom_left_origin = True

            # Create simulation UI
            sim_ui = SimulationUI(
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                menu.selected_scene,
                on_back=lambda: menu.go_to_main_menu(),
                on_reset=lambda: controller.request_reset(),
                on_pause=lambda: controller.toggle_pause() if controller else None,
                on_step=lambda: controller.request_step() if controller else None,
            )

        if menu.state == MenuState.SIMULATION and renderer and sim_ui:
            # Constraints toggle (Rope/Circle scenes)
            renderer.draw_constraints = sim_ui.get_toggle("constraints")

            # Trajectory toggle (Projectile)
            renderer.draw_trajectories = sim_ui.get_toggle("trajectory")

            # Coordinates toggle (Projectile)
            renderer.draw_coordinates = sim_ui.get_toggle("coordinates")

            # Water toggle (Buoyancy)
            renderer.draw_water = sim_ui.get_toggle("water")

            # Scale toggle (All scenes)
            renderer.draw_scale = sim_ui.get_toggle("scale")

        # Cleanup when leaving simulation
        if menu.state != MenuState.SIMULATION and psystem is not None:
            renderer = None
            controller = None
            psystem = None
            sim_ui = None
            interaction = None  # Clear Interaction Handler
            current_scene_module = None
            accumulator = 0.0

        # Update and render
        if menu.state == MenuState.SIMULATION:
            # Update physics
            accumulator += frame_dt

            if controller and controller.should_reset():
                current_scene_module.build(psystem)
                if interaction:
                    interaction.selected_particle = None
                    interaction.dragging_position = False
                    interaction.dragging_velocity = False
                if renderer:
                    renderer.clear_trajectories()
                accumulator = 0.0

            # Step physics
            while accumulator >= FIXED_DT:
                if controller and controller.should_step():
                    psystem.step(FIXED_DT)

                    # Track trajectories for projectile scene
                    if current_scene_module == projectile_scene:
                        for p in psystem.particles:
                            if p.alive:
                                renderer.track_particle_trajectory(
                                    p,
                                    max_points=projectile_config.MAX_TRAIL_POINTS,
                                    trajectory_color=projectile_config.TRAJECTORY_COLOR,
                                )

                accumulator -= FIXED_DT

            # Render simulation
            render_simulation(
                screen,
                renderer,
                psystem,
                sim_ui,
                current_scene_module,
                interaction,
                controller.paused,
            )

            # Draw FPS
            fps_font = pygame.font.SysFont("consolas", 18)
            fps_text = fps_font.render(
                f"FPS: {int(clock.get_fps())}", True, (200, 200, 200)
            )
            screen.blit(fps_text, (10, 10))

        else:
            # Render menu
            menu.draw(screen)

        pygame.display.flip()

    pygame.quit()


def render_simulation(
    screen, renderer, psystem, sim_ui, scene_module, interaction=None, is_paused=False
):
    """Render the simulation screen with physics and UI."""
    from engine.scenes import projectile_config, buoyancy_config

    # Create a subsurface for the simulation area
    sim_width = 1236
    sim_surface = screen.subsurface((0, 0, sim_width, screen.get_height()))

    # Render physics to subsurface
    renderer.screen = sim_surface  # Temporarily redirect rendering
    renderer.begin_frame()

    # Draw scale markers
    if renderer.draw_scale:
        if scene_module.__name__.endswith("projectile_scene"):
            renderer.draw_scale_markers(
                tick_interval=projectile_config.SCALE_TICK_INTERVAL,
                scale_color=projectile_config.SCALE_COLOR,
            )
        elif scene_module.__name__.endswith("buoyancy_scene"):
            renderer.draw_scale_markers(
                tick_interval=buoyancy_config.SCALE_TICK_INTERVAL,
                scale_color=buoyancy_config.SCALE_COLOR,
            )

    # Draw water (buoyancy scene)
    if scene_module.__name__.endswith("buoyancy_scene") and renderer.draw_water:
        SCREEN_HEIGHT = 864.0
        water_top_engine = SCREEN_HEIGHT - buoyancy_config.WATER_Y_TOP
        water_bottom_engine = SCREEN_HEIGHT - buoyancy_config.WATER_Y_BOTTOM

        renderer.draw_water_region(
            water_top=buoyancy_config.WATER_Y_TOP,
            water_bottom=buoyancy_config.WATER_Y_BOTTOM,
            water_color=buoyancy_config.WATER_COLOR,
            surface_color=buoyancy_config.WATER_SURFACE_COLOR,
        )

        # Draw density legend
        if buoyancy_config.SHOW_LEGEND:
            renderer.draw_density_legend(
                x=sim_width - 220,
                y=30,
                low_color=buoyancy_config.COLOR_LOW_DENSITY,
                mid_color=buoyancy_config.COLOR_MID_DENSITY,
                high_color=buoyancy_config.COLOR_HIGH_DENSITY,
                min_density=buoyancy_config.PARTICLE_DENSITY_MIN,
                max_density=buoyancy_config.PARTICLE_DENSITY_MAX,
            )

    # Draw containers
    for container in psystem.containers:
        renderer.draw_container(container)

    # Draw trajectories (projectile scene)
    if (
        scene_module.__name__.endswith("projectile_scene")
        and renderer.draw_trajectories
    ):
        for p in psystem.particles:
            if p.alive:
                renderer.draw_trajectory_trail(
                    p, trajectory_color=projectile_config.TRAJECTORY_COLOR
                )

    # Draw particles
    for p in psystem.particles:
        if p.alive:
            renderer.draw_particle(p)

    # Add interaction highlights strictly after particles
    if interaction and interaction.selected_particle and is_paused:
        renderer.draw_particle_highlight(interaction.selected_particle)
        renderer.draw_velocity_control(interaction.selected_particle)

    # Draw constraints
    if renderer.draw_constraints:
        for constraint in psystem.constraints:
            particles = constraint.get_particles()
            if len(particles) == 2:
                renderer.draw_constraint(particles[0], particles[1])

    # Draw coordinates (projectile scene)
    if scene_module.__name__.endswith("projectile_scene") and renderer.draw_coordinates:
        for p in psystem.particles:
            if p.alive:
                renderer.draw_particle_coordinates(p)

    renderer.draw_playback_indicator(is_paused)

    # Restore full screen
    renderer.screen = screen
    if hasattr(sim_ui, "update"):
        sim_ui.update(psystem, interaction, is_paused)
    # Draw UI panel on top
    sim_ui.draw(screen)


if __name__ == "__main__":
    main()
