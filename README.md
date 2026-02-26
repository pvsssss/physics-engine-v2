# 2D Physics Engine

A custom-built, blazingly slow 2D physics engine and interactive sandbox created entirely from scratch in Python. This project implements its own mathematical foundation, physics solvers, collision detection pipelines, and a fully custom graphical user interface, relying on `pygame` strictly for drawing to the screen and capturing hardware events.

## 📸 Gallery & Demos

### Screenshots
<details>
<summary><b>Click to view Screenshots</b></summary>
<br>
<img src="https://github.com/pvsssss/physics-engine-v2/raw/master/assets/Home%20screen.jpeg" width="80%" alt="Scene Selection Menu">

_Home Screen_
<br><br>

<img src="https://github.com/pvsssss/physics-engine-v2/raw/master/assets/Scene%20Select%20Menu.jpeg" width="80%" alt="Interactive Controls">

_Scene Selection Menu_
<br><br>

<img src="https://github.com/pvsssss/physics-engine-v2/raw/master/assets/config%20bar.jpeg" width="25%" alt="Physics Engine in Action">

_Select a particle to change its properties_
<br><br>
</details>

### Video Showcases

<details>
<summary><b>Click to view Video Demonstrations</b></summary>
<br>

**1. Collision Lab**
<video src="https://github.com/user-attachments/assets/a6405803-bdb7-4dc7-910e-37c3cd71019f" width="80%" controls="controls" muted="muted"></video>
_Chaotic particle behavior constrained inside a circular boundary, highlighting the narrowphase collision detection and stacking stability._
<br><br>

**2. Constraint Chains & Ropes**
<video src="https://github.com/user-attachments/assets/15f10302-ad4e-42d7-8d27-240ee3432944" width="80%" controls="controls" muted="muted"></video>
_A chain of connected particles demonstrating position-based distance constraints solving iteratively to simulate a swinging rope._
<br><br>

**3. Projectile Motion Sandbox**
<video src="https://github.com/user-attachments/assets/93380183-ea83-4b76-94e7-8df97605e470" width="80%" controls="controls" muted="muted"></video>
_Ballistic trajectory simulation tracking a particle's arc while reacting to live adjustments in wind and gravity._
<br><br>

**4. Buoyancy Engine & Fluid Dynamics**
<video src="https://github.com/user-attachments/assets/23fc03d6-5c5f-4585-a008-787536e30cf8" width="80%" controls="controls" muted="muted"></video>
_A demonstration of Archimedes' principle in action, showcasing particles of varying densities floating and sinking in a fluid volume._
<br><br>

**5. Dynamic Particle Manipulation**
<video src="https://github.com/user-attachments/assets/12bcc226-0b82-4b8b-8e86-f2d6f62082d2" width="100%" controls="controls" muted="muted"></video>
_Showcasing the interactive UI, where the user drags particles and uses the slingshot vector tool to apply velocities in real-time._
<br><br>

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
## 📁 Project Structure
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
