"""
Pathfinding algorithms: A*, Greedy Best-First Search, Uniform Cost Search.

All three share the same return contract:
    {
        "explored_count": int,
        "path_length":    int,          # 0 if no path found
        "time_ms":        float,
        "path":           list[Cell],   # start → end, empty if no path
        "visited_order":  list[Cell],   # cells in the order they were closed
    }

Each algorithm uses LOCAL dicts for costs/parents so they never mutate
shared Cell state during a run — safe for back-to-back comparison calls
on the same Grid snapshot.
"""

import heapq
import time
from grid import Cell, Grid
from constants import STATE_START, STATE_END


# ── Helpers ──────────────────────────────────────────────────────────────────

def manhattan(cell: Cell, end: Cell) -> int:
    return abs(cell.row - end.row) + abs(cell.col - end.col)


def _reconstruct(end_key: tuple, parent: dict, cells: dict) -> list[Cell]:
    """Walk parent pointers back to start and return ordered path."""
    path = []
    cur = end_key
    while cur is not None:
        path.append(cells[cur])
        cur = parent.get(cur)
    path.reverse()
    return path


def _make_result(explored: list[Cell], path: list[Cell], elapsed_ms: float) -> dict:
    return {
        "explored_count": len(explored),
        "path_length":    max(0, len(path) - 1),   # edges, not nodes
        "time_ms":        elapsed_ms,
        "path":           path,
        "visited_order":  explored,
    }


# ── A* ───────────────────────────────────────────────────────────────────────

def astar(grid: Grid) -> dict:
    """A* search — priority = g + h (Manhattan)."""
    start, end = grid.start, grid.end
    if start is None or end is None:
        return _make_result([], [], 0.0)

    g: dict[tuple, float] = {}
    parent: dict[tuple, tuple | None] = {}
    cell_map: dict[tuple, Cell] = {}

    sk = (start.row, start.col)
    ek = (end.row, end.col)

    g[sk] = 0
    parent[sk] = None
    cell_map[sk] = start

    h0 = manhattan(start, end)
    heap = [(h0, 0, sk)]   # (f, tie-break counter, key)
    counter = 1
    closed: set[tuple] = set()
    visited_order: list[Cell] = []

    t0 = time.perf_counter()

    while heap:
        f, _, cur_k = heapq.heappop(heap)
        if cur_k in closed:
            continue
        closed.add(cur_k)

        cur_cell = cell_map[cur_k]
        if cur_cell.state not in (STATE_START, STATE_END):
            visited_order.append(cur_cell)

        if cur_k == ek:
            elapsed = (time.perf_counter() - t0) * 1000
            path = _reconstruct(ek, parent, cell_map)
            return _make_result(visited_order, path, elapsed)

        for nb in cur_cell.get_neighbors(grid):
            nk = (nb.row, nb.col)
            new_g = g[cur_k] + 1
            if new_g < g.get(nk, float("inf")):
                g[nk] = new_g
                parent[nk] = cur_k
                cell_map[nk] = nb
                h = manhattan(nb, end)
                heapq.heappush(heap, (new_g + h, counter, nk))
                counter += 1

    elapsed = (time.perf_counter() - t0) * 1000
    return _make_result(visited_order, [], elapsed)


# ── Greedy Best-First Search ─────────────────────────────────────────────────

def greedy_bfs(grid: Grid) -> dict:
    """Greedy Best-First — priority = h only (ignores path cost)."""
    start, end = grid.start, grid.end
    if start is None or end is None:
        return _make_result([], [], 0.0)

    parent: dict[tuple, tuple | None] = {}
    cell_map: dict[tuple, Cell] = {}

    sk = (start.row, start.col)
    ek = (end.row, end.col)

    parent[sk] = None
    cell_map[sk] = start

    heap = [(manhattan(start, end), 0, sk)]
    counter = 1
    closed: set[tuple] = set()
    visited_order: list[Cell] = []

    t0 = time.perf_counter()

    while heap:
        _, _, cur_k = heapq.heappop(heap)
        if cur_k in closed:
            continue
        closed.add(cur_k)

        cur_cell = cell_map[cur_k]
        if cur_cell.state not in (STATE_START, STATE_END):
            visited_order.append(cur_cell)

        if cur_k == ek:
            elapsed = (time.perf_counter() - t0) * 1000
            path = _reconstruct(ek, parent, cell_map)
            return _make_result(visited_order, path, elapsed)

        for nb in cur_cell.get_neighbors(grid):
            nk = (nb.row, nb.col)
            if nk not in closed and nk not in parent:
                parent[nk] = cur_k
                cell_map[nk] = nb
                heapq.heappush(heap, (manhattan(nb, end), counter, nk))
                counter += 1

    elapsed = (time.perf_counter() - t0) * 1000
    return _make_result(visited_order, [], elapsed)


# ── Uniform Cost Search (Dijkstra) ───────────────────────────────────────────

def ucs(grid: Grid) -> dict:
    """UCS / Dijkstra — priority = g only, all edges cost 1."""
    start, end = grid.start, grid.end
    if start is None or end is None:
        return _make_result([], [], 0.0)

    g: dict[tuple, float] = {}
    parent: dict[tuple, tuple | None] = {}
    cell_map: dict[tuple, Cell] = {}

    sk = (start.row, start.col)
    ek = (end.row, end.col)

    g[sk] = 0
    parent[sk] = None
    cell_map[sk] = start

    heap = [(0, 0, sk)]
    counter = 1
    closed: set[tuple] = set()
    visited_order: list[Cell] = []

    t0 = time.perf_counter()

    while heap:
        cost, _, cur_k = heapq.heappop(heap)
        if cur_k in closed:
            continue
        closed.add(cur_k)

        cur_cell = cell_map[cur_k]
        if cur_cell.state not in (STATE_START, STATE_END):
            visited_order.append(cur_cell)

        if cur_k == ek:
            elapsed = (time.perf_counter() - t0) * 1000
            path = _reconstruct(ek, parent, cell_map)
            return _make_result(visited_order, path, elapsed)

        for nb in cur_cell.get_neighbors(grid):
            nk = (nb.row, nb.col)
            new_g = g[cur_k] + 1
            if new_g < g.get(nk, float("inf")):
                g[nk] = new_g
                parent[nk] = cur_k
                cell_map[nk] = nb
                heapq.heappush(heap, (new_g, counter, nk))
                counter += 1

    elapsed = (time.perf_counter() - t0) * 1000
    return _make_result(visited_order, [], elapsed)
