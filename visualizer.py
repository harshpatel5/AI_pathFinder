"""All Pygame rendering: grid, toolbar, sidebar, animation queue."""

import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GRID_AREA_WIDTH, SIDEBAR_WIDTH,
    ROWS, COLS, CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y,
    ANIMATION_SPEED,
    COLOR_BG, COLOR_GRID_LINE, COLOR_SIDEBAR_BG, COLOR_PANEL_BG,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT, COLOR_WARNING,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_BTN_IDLE,
    COLOR_ROW_EVEN, COLOR_ROW_ODD, COLOR_ROW_NO_PATH,
    STATE_COLOR_MAP, STATE_START, STATE_END,
    ALGO_NAMES,
)
from grid import Cell, Grid
from ui import Button


class Visualizer:
    """Owns the Pygame window and all drawing/animation logic."""

    def __init__(self, grid: Grid):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pathfinding Visualizer — A* / Greedy / UCS")

        self.grid = grid

        # Fonts
        self.font_sm  = pygame.font.SysFont("consolas", 11)
        self.font_md  = pygame.font.SysFont("consolas", 12, bold=True)
        self.font_lg  = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_xl  = pygame.font.SysFont("consolas", 16, bold=True)

        # Animation queue: list of (Cell, new_state)
        self._anim_queue: list[tuple[Cell, int]] = []

        # Last algorithm results  {algo_key: result_dict}
        self.results: dict = {}

        # Toolbar mode buttons and sidebar action buttons (set from main.py)
        self.toolbar_buttons: list[Button] = []
        self.sidebar_buttons: list[Button] = []

    # ── Animation ─────────────────────────────────────────────────────────────

    def build_animation_queue(self, visited_order: list[Cell], path: list[Cell]):
        """Convert algorithm output into a step-by-step animation queue."""
        from constants import STATE_OPEN, STATE_CLOSED, STATE_PATH
        queue: list[tuple[Cell, int]] = []
        for cell in visited_order:
            if cell.state not in (STATE_START, STATE_END):
                queue.append((cell, STATE_CLOSED))
        for cell in path:
            if cell.state not in (STATE_START, STATE_END):
                queue.append((cell, STATE_PATH))
        self._anim_queue = queue

    def step_animation(self):
        """Pop up to ANIMATION_SPEED items and update cell states."""
        for _ in range(ANIMATION_SPEED):
            if not self._anim_queue:
                break
            cell, new_state = self._anim_queue.pop(0)
            if cell.state not in (STATE_START, STATE_END):
                cell.state = new_state

    def is_animating(self) -> bool:
        return len(self._anim_queue) > 0

    def clear_animation(self):
        self._anim_queue.clear()

    # ── Main draw ─────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(COLOR_BG)
        self._draw_toolbar_bg()
        self._draw_grid()
        self._draw_sidebar()
        self._draw_toolbar_buttons()

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _draw_toolbar_bg(self):
        toolbar_rect = pygame.Rect(0, 0, GRID_AREA_WIDTH, GRID_OFFSET_Y)
        pygame.draw.rect(self.screen, (20, 20, 28), toolbar_rect)
        pygame.draw.line(
            self.screen, COLOR_GRID_LINE,
            (0, GRID_OFFSET_Y - 1), (GRID_AREA_WIDTH, GRID_OFFSET_Y - 1)
        )
        # Title
        title = self.font_md.render("Pathfinding Visualizer", True, COLOR_ACCENT)
        self.screen.blit(title, (8, 14))

    def _draw_toolbar_buttons(self):
        for btn in self.toolbar_buttons:
            btn.draw(self.screen, self.font_sm)

    # ── Grid ─────────────────────────────────────────────────────────────────

    def _draw_grid(self):
        # Grid background (fills gaps between cells with grid line color)
        grid_rect = pygame.Rect(
            GRID_OFFSET_X, GRID_OFFSET_Y,
            COLS * CELL_SIZE, ROWS * CELL_SIZE,
        )
        pygame.draw.rect(self.screen, COLOR_GRID_LINE, grid_rect)

        for row in self.grid.cells:
            for cell in row:
                self._draw_cell(cell)

    def _draw_cell(self, cell: Cell):
        color = STATE_COLOR_MAP.get(cell.state, (50, 50, 50))
        x = GRID_OFFSET_X + cell.col * CELL_SIZE + 1
        y = GRID_OFFSET_Y + cell.row * CELL_SIZE + 1
        w = h = CELL_SIZE - 2
        pygame.draw.rect(self.screen, color, (x, y, w, h))

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _draw_sidebar(self):
        sx = GRID_AREA_WIDTH
        sidebar_rect = pygame.Rect(sx, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BG, sidebar_rect)
        pygame.draw.line(self.screen, COLOR_ACCENT, (sx, 0), (sx, WINDOW_HEIGHT), 2)

        y = 12
        # Section: title
        title = self.font_xl.render("Controls", True, COLOR_ACCENT)
        self.screen.blit(title, (sx + 12, y))
        y += 26

        # Action buttons
        for btn in self.sidebar_buttons:
            btn.draw(self.screen, self.font_md)

        # Results table
        y = self._results_table_top()
        self._draw_results(y)

        # Legend
        self._draw_legend()

    def _results_table_top(self) -> int:
        """Y position where the results table starts (below buttons)."""
        if self.sidebar_buttons:
            last = self.sidebar_buttons[-1]
            return last.rect.bottom + 20
        return 300

    # ── Results table ─────────────────────────────────────────────────────────

    def _draw_results(self, y: int):
        sx = GRID_AREA_WIDTH + 14
        w  = SIDEBAR_WIDTH - 28

        # Section header
        header = self.font_lg.render("Algorithm Comparison", True, COLOR_ACCENT)
        self.screen.blit(header, (sx, y))
        y += 26

        if not self.results:
            msg = self.font_sm.render("Run an algorithm to see results.", True, COLOR_TEXT_DIM)
            self.screen.blit(msg, (sx, y))
            return

        # Column widths (pixels)
        col_w = [90, 72, 72, 72]
        headers = ["Algorithm", "Explored", "Path Len", "Time (ms)"]

        # Header row
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, (sx - 4, y, w + 8, 22), border_radius=3)
        x = sx
        for i, hdr in enumerate(headers):
            surf = self.font_sm.render(hdr, True, COLOR_TEXT_DIM)
            self.screen.blit(surf, (x + 4, y + 4))
            x += col_w[i]
        y += 22

        # Data rows
        algo_order = ["astar", "greedy", "ucs"]
        for idx, key in enumerate(algo_order):
            if key not in self.results:
                continue
            res = self.results[key]
            no_path = res["path_length"] == 0

            row_color = COLOR_ROW_NO_PATH if no_path else (COLOR_ROW_ODD if idx % 2 else COLOR_ROW_EVEN)
            pygame.draw.rect(self.screen, row_color, (sx - 4, y, w + 8, 22), border_radius=2)

            values = [
                ALGO_NAMES.get(key, key),
                str(res["explored_count"]),
                "N/A" if no_path else str(res["path_length"]),
                f'{res["time_ms"]:.2f}',
            ]
            x = sx
            for i, val in enumerate(values):
                color = COLOR_DANGER if (no_path and i == 2) else COLOR_TEXT
                surf = self.font_sm.render(val, True, color)
                self.screen.blit(surf, (x + 4, y + 4))
                x += col_w[i]
            y += 22

        # Divider
        pygame.draw.line(self.screen, COLOR_GRID_LINE, (sx - 4, y + 6), (sx + w + 4, y + 6))
        y += 16

        # Quick insight
        self._draw_insight(sx, y)

    def _draw_insight(self, sx: int, y: int):
        """Show a one-line insight comparing A* vs others."""
        if len(self.results) < 2:
            return
        lines = []
        if "astar" in self.results and "ucs" in self.results:
            a = self.results["astar"]
            u = self.results["ucs"]
            if u["explored_count"] > 0:
                pct = 100 * (1 - a["explored_count"] / u["explored_count"])
                lines.append(f"A* explores {pct:.0f}% fewer nodes than UCS")
        if "astar" in self.results and "greedy" in self.results:
            a = self.results["astar"]
            g = self.results["greedy"]
            if a["path_length"] > 0 and g["path_length"] > 0:
                if a["path_length"] < g["path_length"]:
                    lines.append("A* finds a shorter path than Greedy")
                elif a["path_length"] == g["path_length"]:
                    lines.append("A* & Greedy found equal-length paths")

        for line in lines[:2]:
            surf = self.font_sm.render(line, True, COLOR_WARNING)
            self.screen.blit(surf, (sx, y))
            y += 17

    # ── Legend ────────────────────────────────────────────────────────────────

    def _draw_legend(self):
        from constants import (
            COLOR_START, COLOR_END, COLOR_WALL,
            COLOR_OPEN, COLOR_CLOSED, COLOR_PATH,
        )
        sx = GRID_AREA_WIDTH + 12
        y  = WINDOW_HEIGHT - 130

        legend_label = self.font_md.render("Legend", True, COLOR_ACCENT)
        self.screen.blit(legend_label, (sx, y))
        y += 18

        items = [
            (COLOR_START,  "Start node"),
            (COLOR_END,    "End node"),
            (COLOR_WALL,   "Wall"),
            (COLOR_OPEN,   "Frontier (open set)"),
            (COLOR_CLOSED, "Visited (closed set)"),
            (COLOR_PATH,   "Shortest path"),
        ]
        for color, label in items:
            pygame.draw.rect(self.screen, color, (sx, y + 2, 10, 10), border_radius=2)
            surf = self.font_sm.render(label, True, COLOR_TEXT_DIM)
            self.screen.blit(surf, (sx + 16, y))
            y += 15

    # ── Status message overlay ────────────────────────────────────────────────

    def draw_status(self, message: str, color=None):
        """Draw a small status message at the bottom of the grid area."""
        if color is None:
            color = COLOR_TEXT_DIM
        surf = self.font_sm.render(message, True, color)
        x = GRID_OFFSET_X + 6
        y = GRID_OFFSET_Y + ROWS * CELL_SIZE - 18
        pygame.draw.rect(self.screen, COLOR_BG, (x - 2, y - 2, surf.get_width() + 8, surf.get_height() + 4))
        self.screen.blit(surf, (x, y))
