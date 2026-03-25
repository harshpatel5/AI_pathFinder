"""
Pathfinding Visualizer — main entry point.

Controls:
  Toolbar modes  : [Wall] [Erase] [Start] [End]
  Sidebar buttons: Run All 3 / Run A* / Run Greedy / Run UCS / Reset Path / Clear Grid
  Keyboard       : C = clear all   R = reset path   ESC = quit
  Mouse          : left-click/drag on grid applies current toolbar mode
"""

import sys
import pygame

from constants import (
    FPS, GRID_AREA_WIDTH, WINDOW_HEIGHT,
    GRID_OFFSET_X, GRID_OFFSET_Y, COLS, ROWS, CELL_SIZE,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_TEXT_DIM,
)
from grid import Grid
from algorithms import astar, greedy_bfs, ucs
from visualizer import Visualizer
from ui import Button


# ── Toolbar mode enum ────────────────────────────────────────────────────────
MODE_WALL  = "wall"
MODE_ERASE = "erase"
MODE_START = "start"
MODE_END   = "end"

TOOLBAR_MODES = [MODE_WALL, MODE_ERASE, MODE_START, MODE_END]
MODE_LABELS   = {MODE_WALL: "Wall", MODE_ERASE: "Erase", MODE_START: "Set Start", MODE_END: "Set End"}


# ── Build toolbar buttons ─────────────────────────────────────────────────────

def build_toolbar_buttons(current_mode_ref: list, viz: Visualizer) -> list[Button]:
    """Create the four mode-select buttons in the grid toolbar area."""
    buttons = []
    bw, bh = 76, 24
    x_start = 200
    gap = 86

    for i, mode in enumerate(TOOLBAR_MODES):
        x = x_start + i * gap
        y = 10

        def make_cb(m=mode):
            def cb():
                current_mode_ref[0] = m
                for btn in viz.toolbar_buttons:
                    btn.active = (btn.label == MODE_LABELS[m])
            return cb

        btn = Button(
            (x, y, bw, bh),
            MODE_LABELS[mode],
            make_cb(),
            active=(mode == current_mode_ref[0]),
        )
        buttons.append(btn)

    return buttons


# ── Build sidebar buttons ─────────────────────────────────────────────────────

def build_sidebar_buttons(grid: Grid, viz: Visualizer, run_fn_ref: list) -> list[Button]:
    """Create the run/clear buttons in the sidebar."""
    sx = GRID_AREA_WIDTH + 12
    bw = 130
    bh = 26
    gap = 7
    y_start = 50

    def make_run(algo_key):
        def cb():
            run_fn_ref[0](algo_key)
        return cb

    specs = [
        ("Run All 3",    make_run("all"),   False),
        ("Run A*",       make_run("astar"), False),
        ("Run Greedy",   make_run("greedy"),False),
        ("Run UCS",      make_run("ucs"),   False),
        ("Reset Path",   lambda: (grid.reset_path_only(), viz.clear_animation(), viz.results.clear()) or None, False),
        ("Clear Grid",   lambda: (grid.clear_all(), viz.clear_animation(), viz.results.clear()) or None, True),
    ]

    buttons = []
    for i, (label, cb, danger) in enumerate(specs):
        row = i // 2
        col = i % 2
        x = sx + col * (bw + gap)
        y = y_start + row * (bh + gap)
        buttons.append(Button((x, y, bw, bh), label, cb, danger=danger))

    return buttons


# ── Run algorithms ────────────────────────────────────────────────────────────

def run_algorithms(key: str, grid: Grid, viz: Visualizer):
    """Run one or all algorithms, store results, kick off animation."""
    if grid.start is None or grid.end is None:
        viz.draw_status("  Set a start and end node first.", color=COLOR_DANGER)
        pygame.display.flip()
        return

    if viz.is_animating():
        return

    grid.reset_path_only()
    viz.results.clear()

    algo_map = {"astar": astar, "greedy": greedy_bfs, "ucs": ucs}

    if key == "all":
        keys_to_run = ["astar", "greedy", "ucs"]
    else:
        keys_to_run = [key]

    for k in keys_to_run:
        viz.results[k] = algo_map[k](grid)

    # Animate the primary result: prefer A*, else first key
    anim_key = "astar" if "astar" in viz.results else keys_to_run[0]
    res = viz.results[anim_key]
    viz.build_animation_queue(res["visited_order"], res["path"])


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    clock = pygame.time.Clock()
    grid  = Grid()
    viz   = Visualizer(grid)

    current_mode = [MODE_WALL]   # mutable ref so callbacks can update it

    # We need run_fn before build_sidebar_buttons, use a ref list
    run_fn_ref = [None]

    def run(key):
        run_algorithms(key, grid, viz)

    run_fn_ref[0] = run

    viz.toolbar_buttons = build_toolbar_buttons(current_mode, viz)
    viz.sidebar_buttons = build_sidebar_buttons(grid, viz, run_fn_ref)

    # Track mouse drag state
    mouse_held   = False
    draw_mode    = None   # "wall" or "erase" — set on MOUSEBUTTONDOWN

    running = True
    status_msg = ("  Wall mode  |  Shift+click → start  |  Ctrl+click → end"
                  "  |  C = clear  R = reset", COLOR_TEXT_DIM)

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    grid.clear_all()
                    viz.clear_animation()
                    viz.results.clear()
                elif event.key == pygame.K_r:
                    grid.reset_path_only()
                    viz.clear_animation()
                    viz.results.clear()

            # ── Toolbar + sidebar button events ──────────────────────────────
            if not viz.is_animating():
                for btn in viz.toolbar_buttons:
                    btn.handle_event(event)
                for btn in viz.sidebar_buttons:
                    btn.handle_event(event)

            # ── Grid mouse interaction ────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not viz.is_animating():
                    pos = event.pos
                    # Only handle if click is within the grid area
                    if pos[0] < GRID_AREA_WIDTH and pos[1] >= GRID_OFFSET_Y:
                        cell = grid.get_cell_at_pixel(*pos)
                        if cell:
                            mode = current_mode[0]
                            if mode == MODE_START:
                                grid.set_start(cell)
                            elif mode == MODE_END:
                                grid.set_end(cell)
                            elif mode == MODE_WALL:
                                grid.set_wall(cell)
                                draw_mode = "wall"
                                mouse_held = True
                            elif mode == MODE_ERASE:
                                grid.erase_wall(cell)
                                draw_mode = "erase"
                                mouse_held = True

            elif event.type == pygame.MOUSEMOTION:
                if mouse_held and not viz.is_animating():
                    pos = event.pos
                    if pos[0] < GRID_AREA_WIDTH and pos[1] >= GRID_OFFSET_Y:
                        cell = grid.get_cell_at_pixel(*pos)
                        if cell:
                            if draw_mode == "wall":
                                grid.set_wall(cell)
                            elif draw_mode == "erase":
                                grid.erase_wall(cell)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_held = False
                draw_mode  = None

        # ── Animation tick ────────────────────────────────────────────────────
        if viz.is_animating():
            viz.step_animation()

        # ── Draw ─────────────────────────────────────────────────────────────
        viz.draw()

        # Status hints
        mode_hints = {
            MODE_WALL:  "Wall mode  — click/drag to draw walls",
            MODE_ERASE: "Erase mode — click/drag to remove walls",
            MODE_START: "Start mode — click a cell to set the start node",
            MODE_END:   "End mode   — click a cell to set the end node",
        }
        hint = mode_hints.get(current_mode[0], "")
        if viz.is_animating():
            hint = "Animating…"
        viz.draw_status(hint, color=COLOR_TEXT_DIM)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
