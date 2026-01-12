import pygame

from engine.render.pygame_renderer import PygameRenderer
from engine.physics.particle_system import ParticleSystem
from engine.physics.particle import Particle
from engine.physics.forces import RadialForce
from engine.math.vec import Vec2
from engine.physics.containers.rectangle_container import RectangleContainer
from engine.core.simulation_controller import SimulationController
from engine.scenes import rope_scene
from engine.scenes import circle_container_scene


def main() -> None:
    pygame.init()

    renderer = PygameRenderer()
    controller = SimulationController()

    psystem = ParticleSystem()

    # gravity = Gravity(Vec2(0.0, 800.0))  # pixels/sec^2

    circle_container_scene.build(psystem)

    # Main loop
    running = True
    clock = pygame.time.Clock()
    FIXED_DT = 1.0 / 120.0  # physics timestep
    accumulator = 0.0

    while running:
        frame_dt = clock.tick(60) / 1000.0
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
        if controller.should_reset():
            circle_container_scene.build(psystem)
            accumulator = 0.0

        # Step physics
        while accumulator >= FIXED_DT:
            if controller.should_step():
                psystem.step(FIXED_DT)
            accumulator -= FIXED_DT

        # Render
        renderer.begin_frame()

        for p in psystem.particles:
            if p.alive:
                renderer.draw_particle(p)

        if renderer.draw_constraints:
            for constraint in psystem.constraints:
                particles = constraint.get_particles()
                if len(particles) == 2:
                    renderer.draw_constraint(particles[0], particles[1])

        for container in psystem.containers:
            renderer.draw_container(container)

        renderer.end_frame(clock.get_fps())

    pygame.quit()


if __name__ == "__main__":
    main()
