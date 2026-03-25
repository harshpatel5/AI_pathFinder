from constants import (
    ROWS, COLS, CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, GRID_AREA_WIDTH,
    STATE_EMPTY, STATE_WALL, STATE_START, STATE_END,
    STATE_OPEN, STATE_CLOSED, STATE_PATH,
)


class Cell:
    """A single cell in the pathfinding grid."""

    __slots__ = ("row", "col", "state", "g", "h", "parent")

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.state = STATE_EMPTY
        self.g: float = float("inf")
        self.h: float = 0.0
        self.parent: "Cell | None" = None

    # Required so heapq can compare Cell objects when f values tie
    def __lt__(self, other: "Cell") -> bool:
        return (self.g + self.h) < (other.g + other.h)

    def reset_pathfinding(self):
        """Clear search costs/parent without touching wall/start/end state."""
        self.g = float("inf")
        self.h = 0.0
        self.parent = None

    def get_neighbors(self, grid: "Grid") -> list["Cell"]:
        """Return the up to 4 non-wall orthogonal neighbours."""
        neighbors = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = self.row + dr, self.col + dc
            if 0 <= nr < grid.rows and 0 <= nc < grid.cols:
                neighbor = grid.cells[nr][nc]
                if neighbor.state != STATE_WALL:
                    neighbors.append(neighbor)
        return neighbors

    def __repr__(self) -> str:  # pragma: no cover
        return f"Cell({self.row},{self.col},state={self.state})"


class Grid:
    """Owns the 2‑D array of cells and all mutation helpers."""

    def __init__(self, rows: int = ROWS, cols: int = COLS):
        self.rows = rows
        self.cols = cols
        self.cells: list[list[Cell]] = [
            [Cell(r, c) for c in range(cols)] for r in range(rows)
        ]
        self.start: Cell | None = None
        self.end:   Cell | None = None

    # ── Accessors ─────────────────────────────────────────────────────────────

    def get_cell(self, row: int, col: int) -> Cell:
        return self.cells[row][col]

    def get_cell_at_pixel(self, x: int, y: int) -> "Cell | None":
        """Convert a mouse position to a Cell, or None if outside the grid."""
        gx = x - GRID_OFFSET_X
        gy = y - GRID_OFFSET_Y
        if gx < 0 or gy < 0:
            return None
        col = gx // CELL_SIZE
        row = gy // CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return None

    # ── Mutations ─────────────────────────────────────────────────────────────

    def set_start(self, cell: Cell):
        if self.start and self.start is not cell:
            self.start.state = STATE_EMPTY
        self.start = cell
        cell.state = STATE_START

    def set_end(self, cell: Cell):
        if self.end and self.end is not cell:
            self.end.state = STATE_EMPTY
        self.end = cell
        cell.state = STATE_END

    def toggle_wall(self, cell: Cell):
        if cell.state == STATE_EMPTY:
            cell.state = STATE_WALL
        elif cell.state == STATE_WALL:
            cell.state = STATE_EMPTY

    def set_wall(self, cell: Cell):
        if cell.state not in (STATE_START, STATE_END):
            cell.state = STATE_WALL

    def erase_wall(self, cell: Cell):
        if cell.state == STATE_WALL:
            cell.state = STATE_EMPTY

    # ── Resets ────────────────────────────────────────────────────────────────

    def clear_all(self):
        """Full reset: removes walls, start, end, search state."""
        for row in self.cells:
            for cell in row:
                cell.state = STATE_EMPTY
                cell.reset_pathfinding()
        self.start = None
        self.end = None

    def reset_path_only(self):
        """Keep walls/start/end; clear OPEN/CLOSED/PATH and costs."""
        path_states = {STATE_OPEN, STATE_CLOSED, STATE_PATH}
        for row in self.cells:
            for cell in row:
                if cell.state in path_states:
                    cell.state = STATE_EMPTY
                cell.reset_pathfinding()
