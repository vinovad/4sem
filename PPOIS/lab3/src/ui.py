import pygame
import math
import random
from typing import List, Optional, Tuple


class Button:
    def __init__(self, x, y, width, height, text, font,
                 color=(80, 40, 130), hover_color=(120, 60, 180), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.scale = 1.0
        self.hover_anim = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.hovered else 0.0
        self.hover_anim += (target - self.hover_anim) * 0.15

    def draw(self, surface):
        scale_factor = 1.0 + self.hover_anim * 0.04
        w = int(self.rect.width * scale_factor)
        h = int(self.rect.height * scale_factor)
        x = self.rect.centerx - w // 2
        y = self.rect.centery - h // 2
        scaled_rect = pygame.Rect(x, y, w, h)
        color = tuple(int(a + (b - a) * self.hover_anim) for a, b in zip(self.color, self.hover_color))
        shadow_rect = scaled_rect.move(3, 4)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=10)
        pygame.draw.rect(surface, color, scaled_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255, 80), scaled_rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)


class ParticleSystem:
    def __init__(self):
        self.particles: List[dict] = []

    def emit(self, x, y, color, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": color,
                "alpha": 255,
                "size": random.uniform(3, 7),
                "life": 1.0,
                "decay": random.uniform(0.03, 0.06)
            })

    def emit_line(self, x1, y1, x2, y2, color, count=20):
        for _ in range(count):
            t = random.random()
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            self.emit(int(x), int(y), color, 2)

    def update(self):
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15
            p["vx"] *= 0.98
            p["life"] -= p["decay"]
            p["alpha"] = int(255 * p["life"])
            p["size"] *= 0.97
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surface):
        for p in self.particles:
            if p["alpha"] > 0 and p["size"] > 0.5:
                size = max(1, int(p["size"]))
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color = p["color"] + (int(p["alpha"]),)
                pygame.draw.circle(s, color, (size, size), size)
                surface.blit(s, (int(p["x"]) - size, int(p["y"]) - size))


class ScorePopup:
    def __init__(self, x, y, score, font, color=(255, 255, 100)):
        self.x = x
        self.y = float(y)
        self.score = score
        self.font = font
        self.color = color
        self.alpha = 255
        self.life = 1.0

    def update(self):
        self.y -= 1.5
        self.life -= 0.025
        self.alpha = int(255 * self.life)

    def is_dead(self):
        return self.life <= 0

    def draw(self, surface):
        if self.alpha <= 0:
            return
        surf = self.font.render(f"+{self.score}", True, self.color)
        surf.set_alpha(self.alpha)
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(surf, rect)


class Dialog:
    def __init__(self, width, height, screen_w, screen_h, title, font_large, font_small):
        self.rect = pygame.Rect((screen_w - width) // 2, (screen_h - height) // 2, width, height)
        self.title = title
        self.font_large = font_large
        self.font_small = font_small
        self.visible = False
        self.input_text = ""
        self.input_active = False
        self.result = None
        btn_y = self.rect.bottom - 70
        self.btn_ok = Button(self.rect.centerx - 120, btn_y, 100, 44, "ОК",
                             font_small, (60, 150, 60), (80, 200, 80))
        self.btn_cancel = Button(self.rect.centerx + 20, btn_y, 100, 44, "Отмена",
                                 font_small, (150, 50, 50), (200, 70, 70))

    def show(self, message="", with_input=False):
        self.visible = True
        self.message = message
        self.input_active = with_input
        self.input_text = ""
        self.result = None

    def handle_event(self, event):
        if not self.visible:
            return None
        mouse = pygame.mouse.get_pos()
        self.btn_ok.update(mouse)
        self.btn_cancel.update(mouse)
        if self.input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.result = "confirm"
                self.visible = False
                return "confirm"
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif len(self.input_text) < 20 and event.unicode.isprintable():
                self.input_text += event.unicode
        if self.btn_ok.handle_event(event):
            self.result = "confirm"
            self.visible = False
            return "confirm"
        if self.btn_cancel.handle_event(event):
            self.result = "cancel"
            self.visible = False
            return "cancel"
        return None

    def draw(self, surface):
        if not self.visible:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        pygame.draw.rect(surface, (30, 15, 55), self.rect, border_radius=15)
        pygame.draw.rect(surface, (120, 60, 200), self.rect, 2, border_radius=15)
        title_surf = self.font_large.render(self.title, True, (255, 220, 100))
        surface.blit(title_surf, (self.rect.centerx - title_surf.get_width() // 2, self.rect.top + 20))
        if hasattr(self, 'message'):
            msg_surf = self.font_small.render(self.message, True, (220, 200, 255))
            surface.blit(msg_surf, (self.rect.centerx - msg_surf.get_width() // 2, self.rect.top + 80))
        if self.input_active:
            input_rect = pygame.Rect(self.rect.left + 40, self.rect.top + 130, self.rect.width - 80, 44)
            pygame.draw.rect(surface, (50, 25, 80), input_rect, border_radius=8)
            pygame.draw.rect(surface, (150, 100, 220), input_rect, 2, border_radius=8)
            cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""
            input_surf = self.font_small.render(self.input_text + cursor, True, (255, 255, 255))
            surface.blit(input_surf, (input_rect.left + 10, input_rect.centery - input_surf.get_height() // 2))
        self.btn_ok.draw(surface)
        self.btn_cancel.draw(surface)
