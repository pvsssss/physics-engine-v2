"""
Configuration for buoyancy simulation scene.

COORDINATE SYSTEM:
- Origin (0, 0) is at the BOTTOM-LEFT corner of the screen
- Positive X points RIGHT
- Positive Y points UP
- Screen dimensions: 1000 units wide × 700 units tall

FORCE SCALING:
- Using 100× lower densities than physical reality
- Using 10× lower gravity
- This creates gentle forces that work with default solver settings
- No per-scene solver tuning required!
"""

from engine.math.vec import Vec2

# ========================================
# WATER PROPERTIES
# ========================================

# Water region bounds (bottom-left origin)
WATER_Y_BOTTOM = 0.0
WATER_Y_TOP = 300.0  # Water surface at 300 units from bottom
WATER_X_LEFT = 0.0
WATER_X_RIGHT = 1000.0

# Water visual appearance
WATER_COLOR = (50, 120, 200, 128)  # Blue with transparency
WATER_SURFACE_COLOR = (100, 150, 220)  # Lighter blue for surface line

# Fluid density (kg/m² in 2D)
# REDUCED 100×: Creates gentle buoyancy forces
FLUID_DENSITY = 10.0

# Water drag coefficient
# Moderate value - enough damping to prevent bobbing
WATER_DRAG_COEFFICIENT = 1.0

# ========================================
# PHYSICS
# ========================================

# Gravity (negative Y = downward)
# REDUCED 10×: Gentler forces that work with default solver
GRAVITY = Vec2(0.0, -980.0)

# Air drag coefficient (above water)
AIR_DRAG_COEFFICIENT = 0.2

# Solver iterations - uses default from particle system (20 or 40)
# No need to override!
SOLVER_ITERATIONS = 40  # Let scene use system default

# ========================================
# PARTICLE SETTINGS
# ========================================

# Number of particles to spawn
PARTICLE_COUNT = 20

# Particle radius range
PARTICLE_RADIUS_MIN = 8.0
PARTICLE_RADIUS_MAX = 18.0

# Particle density range (kg/m²)
# REDUCED 100×: Scaled to match water density
#
# Centered around water density (10.0) for neutral buoyancy:
#   7-9:    Clearly floats (70-90% of water density)
#   9-10:   Lightly floats, mostly submerged
#   10-11:  Neutral buoyancy zone (hover mid-water)
#   11-13:  Clearly sinks (110-130% of water density)
PARTICLE_DENSITY_MIN = 7.0  # 30% lighter than water
PARTICLE_DENSITY_MAX = 13.0  # 30% heavier than water

# Particle spawn region (bottom-left origin)
SPAWN_X_MIN = 100.0
SPAWN_X_MAX = 900.0
SPAWN_Y_MIN = 350.0  # Just above water surface
SPAWN_Y_MAX = 600.0

# Initial velocity range for particles
# Scaled down to match gentler physics
SPAWN_VELOCITY_X_MIN = -30.0
SPAWN_VELOCITY_X_MAX = 30.0
SPAWN_VELOCITY_Y_MIN = -30.0
SPAWN_VELOCITY_Y_MAX = 30.0

# Particle physical properties
PARTICLE_RESTITUTION = 0.2  # Some bounce
PARTICLE_FRICTION = 0.3  # Moderate friction
PARTICLE_DAMPING = 0.01  # Light damping

# Sleep threshold
SLEEP_THRESHOLD = 1.0

# ========================================
# VISUAL SETTINGS
# ========================================

# Color gradient for particle density visualization
COLOR_LOW_DENSITY = (255, 50, 50)  # Red (floats)
COLOR_MID_DENSITY = (150, 50, 200)  # Purple (neutral)
COLOR_HIGH_DENSITY = (50, 100, 255)  # Blue (sinks)

# ========================================
# CONTAINER BOUNDS
# ========================================

CONTAINER_X = 0.0
CONTAINER_Y = 0.0
CONTAINER_WIDTH = 950.0
CONTAINER_HEIGHT = 700.0

# ========================================
# DISPLAY SETTINGS
# ========================================

SHOW_DENSITY_LABELS = False
SHOW_LEGEND = True
SCALE_TICK_INTERVAL = 100.0
SCALE_COLOR = (150, 150, 150)
