"""
Configuration for buoyancy simulation scene.

COORDINATE SYSTEM:
- Origin (0, 0) is at the BOTTOM-LEFT corner of the screen
- Positive X points RIGHT
- Positive Y points UP
- Screen dimensions: 1000 units wide × 700 units tall
"""

from engine.math.vec import Vec2

# ========================================
# WATER PROPERTIES
# ========================================

# Water region bounds (bottom-left origin)
# Water fills the bottom portion of the screen
WATER_Y_BOTTOM = 0.0
WATER_Y_TOP = 300.0  # Water surface at 300 units from bottom
WATER_X_LEFT = 0.0
WATER_X_RIGHT = 1000.0

# Water visual appearance
WATER_COLOR = (50, 120, 200, 128)  # Blue with transparency (R, G, B, Alpha)
WATER_SURFACE_COLOR = (100, 150, 220)  # Lighter blue for surface line

# Fluid density (kg/m² in 2D)
# Water at 20°C ≈ 1000 kg/m³, so in 2D we use similar scale
FLUID_DENSITY = 100.0

# Water drag coefficient
# Higher = more resistance to movement in water
WATER_DRAG_COEFFICIENT = 1.5  # INCREASED: More drag to dampen bobbing

# ========================================
# PHYSICS
# ========================================

# Gravity (negative Y = downward)
GRAVITY = Vec2(0.0, -980.0)

# Air drag coefficient (above water)
# This helps dampen bobbing at the surface
AIR_DRAG_COEFFICIENT = 0.3

# Solver iterations for collision resolution
# Higher = better handling of heavy particles
SOLVER_ITERATIONS = 40  # INCREASED: Prevents sinking through floor

# ========================================
# PARTICLE SETTINGS
# ========================================

# Number of particles to spawn
PARTICLE_COUNT = 15

# Particle radius range
PARTICLE_RADIUS_MIN = 8.0
PARTICLE_RADIUS_MAX = 20.0

# Particle density range (kg/m²)
# Objects with density < fluid density will float
# Objects with density > fluid density will sink
PARTICLE_DENSITY_MIN = 50.0  # Will float (less dense than water)
PARTICLE_DENSITY_MAX = (
    160.0  # Will sink (more dense than water) - REDUCED to prevent extreme forces
)

# Particle spawn region (bottom-left origin)
SPAWN_X_MIN = 100.0
SPAWN_X_MAX = 900.0
SPAWN_Y_MIN = 400.0  # Spawn above water
SPAWN_Y_MAX = 650.0

# Initial velocity range for particles
SPAWN_VELOCITY_X_MIN = -50.0
SPAWN_VELOCITY_X_MAX = 50.0
SPAWN_VELOCITY_Y_MIN = -100.0
SPAWN_VELOCITY_Y_MAX = 100.0

# Particle physical properties
PARTICLE_RESTITUTION = 0.1  # REDUCED: Less bouncy (was 0.3)
PARTICLE_FRICTION = 0.8  # INCREASED: More friction (was 0.5)
PARTICLE_DAMPING = 0.02  # ADDED: Small damping to dissipate energy

# Sleep threshold - particles stop simulating when slow enough
# Lower value = particles settle faster
SLEEP_THRESHOLD = 2.0  # Moderate threshold

# ========================================
# VISUAL SETTINGS
# ========================================

# Color gradient for particle density visualization
# Low density (floats) → Red
# Medium density → Purple
# High density (sinks) → Blue

COLOR_LOW_DENSITY = (255, 50, 50)  # Red
COLOR_MID_DENSITY = (150, 50, 200)  # Purple
COLOR_HIGH_DENSITY = (50, 100, 255)  # Blue

# ========================================
# CONTAINER BOUNDS
# ========================================

# Container dimensions (matches screen)
CONTAINER_X = 0.0
CONTAINER_Y = 0.0
CONTAINER_WIDTH = 1000.0
CONTAINER_HEIGHT = 700.0

# ========================================
# DISPLAY SETTINGS
# ========================================

# Show particle density as text below each particle?
SHOW_DENSITY_LABELS = False

# Show density legend?
SHOW_LEGEND = True

# Scale markers
SCALE_TICK_INTERVAL = 100.0
SCALE_COLOR = (150, 150, 150)
