# Origin: Spherical Maze Lab (`spherical-maze-lab`)

- **Original Container:** `https://github.com/admiralorbiter/the_x_files/tree/main/non-euclidean-geo` (Archived)
- **Date Created:** August 1, 2026
- **Consolidated into Sketchbook:** 2026-09-01
- **Tech Stack:** Python 3.10+, Pygame, NumPy

---

## 1. Concept & Hypothesis

Can non-Euclidean spherical geometry ($S^2$) become perceptually intuitive to a player by keeping the observer fixed at the pole in an azimuthal projection and rotating the entire sphere and its geodesic walls underneath them during navigation?

---

## 2. What Was Built

- **Spherical Geometry Engine:** Geodesic distance calculations, great-circle wall intersections, and holonomy tracking.
- **Azimuthal Projection Renderer:** Real-time player-centered viewport mapping 3D spherical coordinates $(\theta, \phi)$ to 2D screen coordinates.
- **Maze Generation:** Procedural spherical maze carving based on great-circle partitions.
