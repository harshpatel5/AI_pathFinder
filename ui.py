"""Simple Pygame button component."""

import pygame
from constants import (
    COLOR_BTN_IDLE, COLOR_BTN_HOVER, COLOR_BTN_PRESS,
    COLOR_BTN_ACTIVE, COLOR_TEXT, COLOR_TEXT_DIM,
)


class Button:
    """A rectangular clickable button."""

    def __init__(
        self,
        rect: tuple | pygame.Rect,
        label: str,
        callback,
        *,
        active: bool = False,
        danger: bool = False,
        tooltip: str = "",
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.active = active          # toolbar "selected" state
        self.danger = danger          # red tint for destructive actions
        self.tooltip = tooltip

        self._hovered = False
        self._pressed = False

    # ── Event handling ────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if the button was clicked this event."""
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                self._pressed = False
                if self.callback:
                    self.callback()
                return True
            self._pressed = False

        return False

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        if self.active:
            color = COLOR_BTN_ACTIVE
        elif self._pressed:
            color = COLOR_BTN_PRESS
        elif self._hovered:
            color = COLOR_BTN_HOVER
        else:
            if self.danger:
                color = (70, 35, 35)
            else:
                color = COLOR_BTN_IDLE

        pygame.draw.rect(surface, color, self.rect, border_radius=5)

        # subtle border
        border_col = (80, 85, 110) if not self.active else (100, 140, 230)
        pygame.draw.rect(surface, border_col, self.rect, width=1, border_radius=5)

        # label
        text_col = COLOR_TEXT if not self.danger else (240, 100, 100)
        text_surf = font.render(self.label, True, text_col)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
