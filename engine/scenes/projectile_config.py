"""
Configuration for projectile motion scene.
Modify these values to change initial conditions of the projectile.

COORDINATE SYSTEM:
- Origin (0, 0) is at the BOTTOM-LEFT corner of the screen
- Positive X points RIGHT
- Positive Y points UP
- Screen dimensions: 1000 units wide  700 units tall
"""

from engine.math.vec import Vec2

# Starting position (x, y) with origin at BOTTOM-LEFT
# Example: Vec2(100, 100) means 100 units right, 100 units up from bottom-left corner
INITIAL_POSITION = Vec2(100.0, 100.0)

# Initial velocity (vx, vy) in units per second
# Positive vx = rightward, Positive vy = upward
INITIAL_VELOCITY = Vec2(300.0, 500.0)

# Gravity acceleration (x, y) in units per second squared
# Standard setup: Vec2(0.0, -980.0) for downward gravity
# Note: Negative Y because gravity pulls DOWN
GRAVITY = Vec2(0.0, -980.0)

# Wind force (constant horizontal force)
# Positive x = rightward wind, Negative x = leftward wind
# Set to Vec2(0.0, 0.0) for no wind
WIND_FORCE = Vec2(0.0, 0.0)

# Particle visual radius (pixels)
PARTICLE_RADIUS = 10.0

# Particle mass (kg)
PARTICLE_MASS = 1.0

# Restitution (bounciness): 0.0 = no bounce, 1.0 = perfect bounce
# Only applies if ENABLE_BOUNCE is True
RESTITUTION = 0.7

# Friction coefficient (0.0 = no friction, 1.0 = high friction)
FRICTION = 0.2
# Air resistance damping (0.0 = no damping, 0.1 = high damping)
DAMPING = 0.0

# Should the particle bounce off container walls?
ENABLE_BOUNCE = True

# Draw trajectory trail behind particle?
DRAW_TRAJECTORY = True

# Maximum number of trail points to keep (prevents memory issues)
MAX_TRAIL_POINTS = 1000

# Container dimensions (matches screen by default)
# These are in bottom-left origin coordinates
CONTAINER_X = 0.0
CONTAINER_Y = 0.0
CONTAINER_WIDTH = 950.0
CONTAINER_HEIGHT = 700.0

# Distance between scale tick marks (in world units)
SCALE_TICK_INTERVAL = 100.0

# Color for scale markings (R, G, B)
SCALE_COLOR = (150, 150, 150)

# Color for trajectory trail (R, G, B)
TRAJECTORY_COLOR = (255, 100, 100)
