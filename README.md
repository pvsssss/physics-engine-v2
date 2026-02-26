# 2D Physics Engine

A custom-built, blazingly slow 2D physics engine and interactive sandbox created entirely from scratch in Python. This project implements its own mathematical foundation, physics solvers, collision detection pipelines, and a fully custom graphical user interface, relying on `pygame` strictly for drawing to the screen and capturing hardware events.

## 📸 Gallery & Demos

_(Add your project screenshots and GIF demonstrations here!)_

### Screenshots

![Scene Selection Menu](link-to-scene-select-image.png)
_The dynamic scene selection menu._

![Interactive Controls](link-to-ui-image.png)
_Live configuration panel and interactive velocity vector editing._

### Video Showcases

<details>
<sunmmary>
- **▶️ [Watch the Buoyancy Engine in Action](./assets/buoayancy%20scene.mp4)**
- **▶️ [Dynamic Particle Manipulation](./assets/sidebar%20config.mp4)**
</sunmmary>
</details>

---

## ✨ Key Features

### ⚙️ Physics Core

- **Integration:** High-stability Velocity Verlet integration for reliable energy conservation.
- **Solver:** Iterative impulse-based solver with Coulomb friction, restitution (bounciness), and positional correction to prevent particle sinking/overlap.
- **Collision Pipeline:** Highly optimized Spatial Hash Grid for Broadphase culling, paired with precise narrowphase math for circle-circle and container boundary collisions.
- **Fluid Dynamics:** Mathematically accurate Archimedes' principle implementation calculating exact submerged circular areas for buoyancy, coupled with quadratic water drag.
- **Constraints:** Position-based distance constraints for simulating rigid sticks and flexible ropes.

### 🖥️ Custom UI Framework

- **Built from Scratch:** A complete UI toolkit built over raw Pygame surfaces without external GUI libraries.
- **Components:** Includes interactive Buttons (with tactile press animations), Sliders, numeric SpinBoxes, and full keyboard-handling Text Inputs.
- **Scrollable Containers:** Features a complex scrolling panel utilizing clipping masks to cleanly hide out-of-bounds nested elements.
- **Live Configuration:** Bi-directional sync allows users to drag particles in the world while text boxes update in real-time, or type specific math into the text boxes to instantly teleport particles.

### 🖐️ Interactive Sandbox

When the simulation is paused, the user can reach directly into the engine:

- **Drag & Drop:** Click and hold any particle to translate its position in world space.
- **Velocity Slingshot:** Grab the visual velocity vector arrowhead of any particle and drag it to dynamically calculate and apply new directional forces.

```text
python-physics-engine/
├── main.py          # Main application entry point and game loop
├── assets/                    # Fonts, icons, and static resources
│   └── LilitaOne-Regular.ttf
└── engine/                    # Core Engine Package
    ├── core/                  # High-level managers and state control
    │   ├── config_manager.py  # Handles active memory and resetting of scene configs
    │   ├── interaction.py     # Mouse picking, dragging, and velocity slingshot math
    │   └── simulation_controller.py
    ├── math/                  # Custom math libraries
    │   └── vec.py             # Custom 2D Vector mathematics
    ├── physics/               # The actual physics engine
    │   ├── particle.py        # Base physics object
    │   ├── particle_system.py # World state and physics stepping
    │   ├── forces.py          # Gravity, Drag, Buoyancy, and Wind formulas
    │   ├── solver.py          # Iterative impulse solver for collisions
    │   ├── broadphase.py      # Spatial Hash Grid for collision optimization
    │   ├── circle_circle.py   # Narrowphase particle collision math
    │   ├── constraints/       # Distance and rigid constraints
    │   └── containers/        # Bounding boxes and circular arenas
    ├── render/                # Pygame drawing layer
    │   ├── pygame_renderer.py # Handles all visual output (shapes, colors, UI overlays)
    │   └── camera.py          # Viewport scaling and Cartesian coordinate conversion
    ├── scenes/                # Pre-built sandbox environments
    │   ├── buoyancy_scene.py  # Fluid dynamics setup
    │   ├── projectile_scene.py# Ballistics setup
    │   ├── rope_scene.py      # Constraint chain setup
    │   └── circle_container_scene.py
    └── ui/                    # Custom User Interface framework
        ├── ui_framework.py    # Base Widgets, ScrollAreas, TextInputs, and Sliders
        ├── menu_system.py     # Menu states, Grid layouts, and Side Panel logic
        └── scene_thumbnails.py# Procedural generation for the scene selection cards
```

---

## 🎮 Included Scenes

1.  **Projectile Motion:** A ballistic trajectory sandbox featuring adjustable wind forces, gravity, and live trajectory trail tracking.
2.  **Buoyancy & Fluid Dynamics:** A water tank simulation where particles of varying densities (colored red to blue) naturally float, sink, or hover based on real area-mass calculations.
3.  **Rope Chain:** A demonstration of iterative position-based constraints mimicking a swinging rope pinned to a ceiling.
4.  **Circle Container:** A chaotic environment where particles are trapped and bounce dynamically inside a curved boundary.

---

## ⌨️ Controls & Keybinds

| Key       | Action                                                          |
| :-------- | :-------------------------------------------------------------- |
| **SPACE** | Play / Pause the simulation                                     |
| **S**     | Step forward exactly one physics frame (when paused)            |
| **R**     | Reset the scene (keeps your custom UI configurations)           |
| **W**     | Hard Reset Config (wipes memory and restores default variables) |
| **C**     | Toggle Constraints visibility                                   |
| **T**     | Toggle Trajectory lines                                         |
| **O**     | Toggle Coordinate labels                                        |
| **L**     | Toggle Scale markers                                            |
| **Q**     | Toggle Water rendering                                          |
| **ESC**   | Return to Main Menu / Quit                                      |

**Mouse Interactions (While Paused):**

- **Left Click + Drag (Particle):** Move a particle's position.
- **Left Click + Drag (Vector Arrow):** Adjust a particle's velocity visually.
- **Scroll Wheel:** Navigate the right-hand Configuration Panel.

---

## 🛠️ Installation & Setup

1. Clone the repository:

```bash
git clone [https://github.com/yourusername/python-physics-engine.git](https://github.com/yourusername/python-physics-engine.git)
cd python-physics-engine
```

2. Ensure you have Python 3.x installed.
3. Install the required dependencies:

```bash
pip install pygame
```

4. Run the engine:

```Bash
python main_with_menu.py
```

---

## 📄 License

This project is open-source and available under the MIT License.
