# ── Window ──────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 920
WINDOW_HEIGHT = 660
GRID_AREA_WIDTH = 600   # left panel
SIDEBAR_WIDTH   = 320   # right panel

# ── Grid ─────────────────────────────────────────────────────────────────────
ROWS = 30
COLS = 30
CELL_SIZE = GRID_AREA_WIDTH // COLS   # 20 px

GRID_OFFSET_X = 0
GRID_OFFSET_Y = 44   # leave room for toolbar at top
# Grid fits: 44 + 30*20 = 644 px ≤ 660 WINDOW_HEIGHT ✓

# ── Timing ───────────────────────────────────────────────────────────────────
FPS             = 60
ANIMATION_SPEED = 4   # cells popped from animation queue per frame

# ── Cell state constants ─────────────────────────────────────────────────────
STATE_EMPTY  = 0
STATE_WALL   = 1
STATE_START  = 2
STATE_END    = 3
STATE_OPEN   = 4
STATE_CLOSED = 5
STATE_PATH   = 6

# ── Colors (R, G, B) ─────────────────────────────────────────────────────────
COLOR_BG          = (18,  18,  18)
COLOR_GRID_LINE   = (38,  38,  38)
COLOR_EMPTY       = (28,  28,  30)
COLOR_WALL        = (58,  60,  62)
COLOR_START       = (39, 195,  94)
COLOR_END         = (220,  55,  55)
COLOR_OPEN        = (70, 130, 220)
COLOR_CLOSED      = (50,  55, 110)
COLOR_PATH        = (255, 210,  40)

COLOR_SIDEBAR_BG  = (22,  22,  32)
COLOR_PANEL_BG    = (30,  30,  44)
COLOR_TEXT        = (210, 210, 218)
COLOR_TEXT_DIM    = (110, 110, 130)
COLOR_ACCENT      = (80, 120, 220)
COLOR_SUCCESS     = (39, 195,  94)
COLOR_DANGER      = (220,  55,  55)
COLOR_WARNING     = (255, 180,  40)

COLOR_BTN_IDLE    = (45,  50,  68)
COLOR_BTN_HOVER   = (65,  72,  98)
COLOR_BTN_PRESS   = (35,  40,  55)
COLOR_BTN_ACTIVE  = (60,  90, 170)   # toolbar mode active state

COLOR_ROW_EVEN    = (30,  30,  46)
COLOR_ROW_ODD     = (26,  26,  40)
COLOR_ROW_NO_PATH = (55,  28,  28)

# ── State → Color map ─────────────────────────────────────────────────────────
STATE_COLOR_MAP = {
    STATE_EMPTY:  COLOR_EMPTY,
    STATE_WALL:   COLOR_WALL,
    STATE_START:  COLOR_START,
    STATE_END:    COLOR_END,
    STATE_OPEN:   COLOR_OPEN,
    STATE_CLOSED: COLOR_CLOSED,
    STATE_PATH:   COLOR_PATH,
}

# ── Algorithm display names ───────────────────────────────────────────────────
ALGO_NAMES = {
    "astar":   "A*",
    "greedy":  "Greedy",
    "ucs":     "UCS",
}
