import pygame

from engine.render.pygame_renderer import PygameRenderer
from engine.physics.particle_system import ParticleSystem
from engine.core.simulation_controller import SimulationController
from engine.scenes import rope_scene
from engine.scenes import circle_container_scene
from engine.scenes import projectile_scene
from engine.scenes import projectile_config
from engine.scenes import buoyancy_scene
from engine.scenes import buoyancy_config


def main() -> None:
    pygame.init()

    renderer = PygameRenderer()
    controller = SimulationController()
    psystem = ParticleSystem()

    # enter your scene here
    scene = projectile_scene
    # scene_config = buoyancy_config
    scene.build(psystem)

    if scene == projectile_scene:
        renderer.draw_trajectories = projectile_config.DRAW_TRAJECTORY
        renderer.draw_coordinates = True
        renderer.draw_scale = True
        renderer.draw_containers = False
        # Enable bottom-left origin coordinate system for projectile scene
        renderer.use_bottom_left_origin = True

    if scene == buoyancy_scene:
        renderer.draw_water = True
        renderer.draw_scale = True
        renderer.draw_containers = False
        renderer.use_bottom_left_origin = True
        SCREEN_HEIGHT = 700.0
        water_bottom_engine = SCREEN_HEIGHT - buoyancy_config.WATER_Y_BOTTOM
        water_top_engine = SCREEN_HEIGHT - buoyancy_config.WATER_Y_TOP

    # Main loop
    running = True
    clock = pygame.time.Clock()
    FIXED_DT = 1.0 / 144.0  # physics timestep
    accumulator = 0.0

    while running:
        frame_dt = clock.tick(144) / 1000.0
        accumulator += frame_dt

        # keyboard event controller
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
                elif event.key == pygame.K_t:  # Toggle trajectory
                    renderer.draw_trajectories = not renderer.draw_trajectories
                elif event.key == pygame.K_o:  # Toggle coordinates
                    renderer.draw_coordinates = not renderer.draw_coordinates
                elif event.key == pygame.K_l:  # Toggle scale
                    renderer.draw_scale = not renderer.draw_scale

        if controller.should_reset():
            scene.build(psystem)
            renderer.clear_trajectories()  # Clear old trajectory
            accumulator = 0.0

        # Step physics
        while accumulator >= FIXED_DT:
            if controller.should_step():
                psystem.step(FIXED_DT)

                # Track trajectory for all particles
                for p in psystem.particles:
                    if p.alive:
                        renderer.track_particle_trajectory(
                            p,
                            max_points=projectile_config.MAX_TRAIL_POINTS,
                            trajectory_color=projectile_config.TRAJECTORY_COLOR,
                        )

            accumulator -= FIXED_DT

        # Render
        renderer.begin_frame()

        # draw containers
        for container in psystem.containers:
            renderer.draw_container(container)

        # drawing scale marker
        renderer.draw_scale_markers(
            tick_interval=projectile_config.SCALE_TICK_INTERVAL,
            scale_color=projectile_config.SCALE_COLOR,
        )
        if scene == buoyancy_scene:
            renderer.draw_water_region(
                water_top=water_top_engine,
                water_bottom=water_bottom_engine,
                water_color=buoyancy_config.WATER_COLOR,
                surface_color=buoyancy_config.WATER_SURFACE_COLOR,
            )
        # Draw trajectory trails
        for p in psystem.particles:
            if p.alive:
                renderer.draw_trajectory_trail(
                    p, trajectory_color=projectile_config.TRAJECTORY_COLOR
                )

        # Draw particles
        for p in psystem.particles:
            if p.alive:
                renderer.draw_particle(p)

        # Draw constraints
        if renderer.draw_constraints:
            for constraint in psystem.constraints:
                particles = constraint.get_particles()
                if len(particles) == 2:
                    renderer.draw_constraint(particles[0], particles[1])

        # Draw particle coordinates (foreground layer)
        for p in psystem.particles:
            if p.alive:
                renderer.draw_particle_coordinates(p)

        renderer.end_frame(clock.get_fps())

    pygame.quit()


if __name__ == "__main__":
    main()
