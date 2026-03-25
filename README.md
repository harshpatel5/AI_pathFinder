# SOFE 3720: Introduction to Artificial Intelligence @ Ontario Tech University.
# Final project: Pathfinding Visualizer

An interactive pathfinding visualizer built with Python and Pygame. Watch A*, Greedy Best-First Search, and Uniform Cost Search (UCS) navigate a 2D grid in real time - and compare their performance side by side.
 
## Demo

- Draw walls, place a start and end node, then run any of the three algorithms
- Watch the exploration animate live on the grid
- Compare nodes explored, path length, and runtime across all three algorithms instantly

## Algorithms Implemented

| Algorithm | Strategy | Optimal? | Heuristic |
|---|---|---|---|
| A* | f(n) = g(n) + h(n) | Yes | Manhattan distance |
| Greedy Best-First | f(n) = h(n) only | No | Manhattan distance |
| Uniform Cost Search | f(n) = g(n) only | Yes | None |

All three are implemented from scratch using Python's `heapq` module - no pathfinding libraries used.

## Features

- Interactive 30×30 grid; click and drag to draw or erase walls
- Place start and end nodes anywhere on the grid
- Run a single algorithm or all three at once
- Live animation of the exploration and final path
- Sidebar comparison table showing nodes explored, path length, and runtime
- Automatic insights: e.g. "A* explores 60% fewer nodes than UCS"
- Reset path or clear the full grid without restarting

## Controls

| Input | Action |
|---|---|
| Wall mode + click/drag | Draw walls |
| Erase mode + click/drag | Remove walls |
| Start mode + click | Place start node |
| End mode + click | Place end node |
| Run A* / Greedy / UCS | Run a single algorithm |
| Run All 3 | Run all algorithms and compare |
| Reset Path | Clear exploration, keep walls |
| Clear Grid | Reset everything |
| R | Reset path (keyboard shortcut) |
| C | Clear grid (keyboard shortcut) |
| ESC | Quit |


## Project Structure
```
pathfinder/
├── main.py          # Entry point — event loop, button setup, mouse handling
├── algorithms.py    # A*, Greedy Best-First, and UCS implementations
├── grid.py          # Cell and Grid data model
├── visualizer.py    # All Pygame rendering and animation logic
├── ui.py            # Reusable Button component
├── constants.py     # Grid size, colours, state codes, timing config
└── requirements.txt # Dependencies
```


## Installation and Setup

**1. Clone the repository**
```bash
git clone https://github.com/harshpatel5/AI_pathFinder.git
cd AI_pathFinder
```

**2. Install dependencies**
```bash
pip install pygame
```
Or using the requirements file:
```bash
pip install -r requirements.txt
```

**3. Run the project**
```bash
python main.py
```
> Requires Python 3.10 or higher.

## How It Works

The grid is a 30×30 array of `Cell` objects. Each cell tracks its position and state (empty, wall, start, end, open, closed, path).

When an algorithm runs, it uses **local cost dictionaries** rather than writing to cell attributes - this means all three algorithms can run back-to-back on the same grid without any state bleed between runs.

The search result (visited order + path) is handed to the `Visualizer`, which converts it into a frame-by-frame animation queue and renders it at 60 FPS.

### A* and the Manhattan Heuristic
```
f(n) = g(n) + h(n)
h(n) = |row_n - row_goal| + |col_n - col_goal|
```

The Manhattan distance is admissible (which means it never overestimates) and consistent, guaranteeing A* finds the optimal path. Compared to UCS, A* typically explores 40–70% fewer nodes on open grids.


## Requirements

- Python 3.10+
- pygame >= 2.5.0


## Authors

- Harsh Patel
- Prabhnoor Saini
- Khushi Patel

Ontario Tech University - SOFE 3720, March 2025
