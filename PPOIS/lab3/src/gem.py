import pygame
import math
import json
import os
from typing import Optional, Tuple

_gems_config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "gems.json")
with open(_gems_config_path, "r", encoding="utf-8") as f:
    GEMS_CONFIG = json.load(f)

GEM_COLORS = {k: tuple(v["color"]) for k, v in GEMS_CONFIG["gems"].items()}
SPECIAL_CONFIG = GEMS_CONFIG["special_gems"]


class Gem:
    NORMAL = "normal"
    BOMB = "bomb"
    LIGHTNING = "lightning"
    STAR = "star"

    def __init__(self, gem_type: str, row: int, col: int, cell_size: int, special: str = NORMAL):
        self.gem_type = gem_type
        self.special = special
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.scale = 0.0
        self.alpha = 255
        self.is_appearing = True
        self.appear_speed = 0.12
        self.is_destroying = False
        self.destroy_progress = 0.0
        self.destroy_speed = 0.1
        self.is_moving = False
        self.pulse_phase = (row * 7 + col * 13) % 100 / 100 * math.pi * 2
        self.selected = False

    @property
    def color(self) -> Tuple[int, int, int]:
        if self.special == Gem.BOMB:
            return tuple(SPECIAL_CONFIG["bomb"]["color"])
        elif self.special == Gem.LIGHTNING:
            return tuple(SPECIAL_CONFIG["lightning"]["color"])
        elif self.special == Gem.STAR:
            return tuple(SPECIAL_CONFIG["star"]["color"])
        return GEM_COLORS.get(self.gem_type, (200, 200, 200))

    def update(self, dt: float):
        self.pulse_phase += dt * 2.0
        if self.is_appearing:
            self.scale = min(1.0, self.scale + self.appear_speed)
            if self.scale >= 1.0:
                self.is_appearing = False
        if self.is_destroying:
            self.destroy_progress = min(1.0, self.destroy_progress + self.destroy_speed)
            self.alpha = int(255 * (1.0 - self.destroy_progress))
            self.scale = 1.0 + self.destroy_progress * 0.3

    def start_destroy(self):
        self.is_destroying = True
        self.destroy_progress = 0.0

    def is_dead(self) -> bool:
        return self.is_destroying and self.destroy_progress >= 1.0

    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int, cell_size: int, time: float):
        px = offset_x + self.col * cell_size + cell_size // 2 + self.x
        py = offset_y + self.row * cell_size + cell_size // 2 + self.y
        base_size = int(cell_size * 0.42 * self.scale)
        if base_size <= 0:
            return
        pulse = 0
        if self.selected:
            pulse = int(math.sin(self.pulse_phase * 3) * 3)
        size = base_size + pulse
        gem_surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
        cx, cy = size + 2, size + 2
        base_color = self.color
        shadow_surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 60), (cx + 3, cy + 3), size)
        surface.blit(shadow_surf, (px - cx, py - cy))
        self._draw_gem_shape(gem_surf, cx, cy, size, base_color)
        highlight_color = tuple(min(255, c + 80) for c in base_color) + (180,)
        pygame.draw.ellipse(gem_surf, highlight_color, (cx - size // 2, cy - size // 2, size // 2, size // 3))
        if self.special != Gem.NORMAL:
            self._draw_special_icon(gem_surf, cx, cy, size)
        if self.alpha < 255:
            gem_surf.set_alpha(self.alpha)
        surface.blit(gem_surf, (px - cx, py - cy))
        if self.selected:
            pygame.draw.circle(surface, (255, 255, 255), (px, py), size + 4, 2)

    def _draw_gem_shape(self, surf, cx, cy, size, color):
        k = 0.7
        points = [
            (cx, cy - size),
            (cx + int(size * k), cy - int(size * k * 0.4)),
            (cx + size, cy),
            (cx + int(size * k), cy + int(size * k * 0.4)),
            (cx, cy + size),
            (cx - int(size * k), cy + int(size * k * 0.4)),
            (cx - size, cy),
            (cx - int(size * k), cy - int(size * k * 0.4)),
        ]
        r, g, b = color
        dark = (max(0, r - 50), max(0, g - 50), max(0, b - 50))
        light = (min(255, r + 60), min(255, g + 60), min(255, b + 60))
        pygame.draw.polygon(surf, dark, points)
        inner_points = [(cx + (px - cx) * 0.7, cy + (py - cy) * 0.7) for px, py in points]
        pygame.draw.polygon(surf, light, [(int(x), int(y)) for x, y in inner_points])
        pygame.draw.polygon(surf, color, points, 2)

    def _draw_special_icon(self, surf, cx, cy, size):
        icon_size = max(4, size // 3)
        if self.special == Gem.BOMB:
            pygame.draw.circle(surf, (255, 50, 0, 200), (cx, cy), icon_size)
            pygame.draw.line(surf, (255, 200, 0), (cx, cy - icon_size),
                             (cx + icon_size // 2, cy - icon_size - icon_size // 2), 2)
        elif self.special == Gem.LIGHTNING:
            pts = [
                (cx + icon_size // 2, cy - icon_size),
                (cx - icon_size // 4, cy - icon_size // 4),
                (cx + icon_size // 4, cy - icon_size // 4),
                (cx - icon_size // 2, cy + icon_size),
                (cx + icon_size // 4, cy + icon_size // 4),
                (cx - icon_size // 4, cy + icon_size // 4),
            ]
            pygame.draw.polygon(surf, (255, 255, 0, 220), pts)
        elif self.special == Gem.STAR:
            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                x1 = cx + int(math.cos(rad) * icon_size)
                y1 = cy + int(math.sin(rad) * icon_size)
                pygame.draw.line(surf, (255, 215, 0, 220), (cx, cy), (x1, y1), 2)
