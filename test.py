import pygame

from engine.render.pygame_renderer import PygameRenderer
from engine.physics.particle_system import ParticleSystem
from engine.core.simulation_controller import SimulationController
from engine.scenes import rope_scene
from engine.scenes import circle_container_scene
from engine.scenes import projectile_scene
from engine.scenes import buoyancy_scene
from engine.scenes import buoyancy_config


def main() -> None:
    pygame.init()

    renderer = PygameRenderer()
    controller = SimulationController()
    psystem = ParticleSystem()

    # Use buoyancy scene
    scene = buoyancy_scene
    scene.build(psystem)

    # Enable buoyancy-specific rendering features
    renderer.draw_water = True
    renderer.draw_scale = True
    renderer.use_bottom_left_origin = True

    # Main loop
    running = True
    clock = pygame.time.Clock()
    FIXED_DT = 1.0 / 144.0  # physics timestep
    accumulator = 0.0

    # Convert water bounds to engine coordinates for rendering
    SCREEN_HEIGHT = 700.0
    water_top_engine = SCREEN_HEIGHT - buoyancy_config.WATER_Y_TOP
    water_bottom_engine = SCREEN_HEIGHT - buoyancy_config.WATER_Y_BOTTOM

    while running:
        frame_dt = clock.tick(144) / 1000.0
        accumulator += frame_dt

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    controller.toggle_pause()
                elif event.key == pygame.K_s:
                    controller.request_step()
                elif event.key == pygame.K_r:
                    controller.request_reset()
                elif event.key == pygame.K_c:  # Toggle constraints
                    renderer.draw_constraints = not renderer.draw_constraints
                elif event.key == pygame.K_w:  # Toggle water visualization
                    renderer.draw_water = not renderer.draw_water
                elif event.key == pygame.K_l:  # Toggle scale
                    renderer.draw_scale = not renderer.draw_scale

        if controller.should_reset():
            scene.build(psystem)
            accumulator = 0.0

        # Step physics
        while accumulator >= FIXED_DT:
            if controller.should_step():
                psystem.step(FIXED_DT)
            accumulator -= FIXED_DT

        # Render
        renderer.begin_frame()

        # Draw scale markers (background layer)
        renderer.draw_scale_markers(
            tick_interval=buoyancy_config.SCALE_TICK_INTERVAL,
            scale_color=buoyancy_config.SCALE_COLOR,
        )

        # Draw water region
        renderer.draw_water_region(
            water_top=water_top_engine,
            water_bottom=water_bottom_engine,
            water_color=buoyancy_config.WATER_COLOR,
            surface_color=buoyancy_config.WATER_SURFACE_COLOR,
        )

        # Draw containers
        for container in psystem.containers:
            renderer.draw_container(container)

        # Draw particles (they have custom colors)
        for p in psystem.particles:
            if p.alive:
                renderer.draw_particle(p)

        # Draw constraints (if any)
        if renderer.draw_constraints:
            for constraint in psystem.constraints:
                particles = constraint.get_particles()
                if len(particles) == 2:
                    renderer.draw_constraint(particles[0], particles[1])

        # Draw density legend
        if buoyancy_config.SHOW_LEGEND:
            renderer.draw_density_legend(
                x=SCREEN_WIDTH - 220,
                y=20,
                low_color=buoyancy_config.COLOR_LOW_DENSITY,
                mid_color=buoyancy_config.COLOR_MID_DENSITY,
                high_color=buoyancy_config.COLOR_HIGH_DENSITY,
                min_density=buoyancy_config.PARTICLE_DENSITY_MIN,
                max_density=buoyancy_config.PARTICLE_DENSITY_MAX,
            )

        renderer.end_frame(clock.get_fps())

    pygame.quit()


if __name__ == "__main__":
    main()
