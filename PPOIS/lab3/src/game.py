import pygame
import json
import os
import math
from typing import Optional

from src.board import Board
from src.gem import Gem, GEM_COLORS
from src.ui import Button, ParticleSystem, ScorePopup, Dialog
from src.sound_manager import SoundManager
from src.highscores import HighScores


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


BASE = os.path.dirname(os.path.dirname(__file__))
SETTINGS = _load_json(os.path.join(BASE, "configs", "settings.json"))
LEVELS_CONFIG = _load_json(os.path.join(BASE, "configs", "levels.json"))


class Game:
    MENU = "menu"
    MODE_SELECT = "mode_select"
    PLAYING = "playing"
    HIGHSCORES = "highscores"
    HELP = "help"
    GAME_OVER = "game_over"

    def __init__(self):
        cfg = SETTINGS["window"]
        self.screen_w = cfg["width"]
        self.screen_h = cfg["height"]
        self.fps = cfg["fps"]
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption(cfg["title"])
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = self.MENU
        self.game_time = 0.0
        self.font_xl = pygame.font.SysFont("segoeui", 56, bold=True)
        self.font_lg = pygame.font.SysFont("segoeui", 36, bold=True)
        self.font_md = pygame.font.SysFont("segoeui", 26)
        self.font_sm = pygame.font.SysFont("segoeui", 20)
        self.sound = SoundManager()
        self.highscores = HighScores()
        self.board: Optional[Board] = None
        self.score = 0
        self.combo = 0
        self.game_mode = None
        self.current_level = 0
        self.time_left = 0.0
        self.level_target = 0
        self.particles = ParticleSystem()
        self.score_popups = []
        self.score_dialog = Dialog(400, 280, self.screen_w, self.screen_h,
                                   "🏆 Новый рекорд!", self.font_lg, self.font_md)
        self.bg_particles = [self._new_bg_particle() for _ in range(60)]
        self._build_menu()
        self.sound.play_music()

    def _new_bg_particle(self):
        import random
        return {
            "x": random.uniform(0, self.screen_w),
            "y": random.uniform(0, self.screen_h),
            "vx": random.uniform(-0.4, 0.4),
            "vy": random.uniform(-0.6, -0.1),
            "size": random.uniform(1, 4),
            "color": random.choice([(200, 100, 255), (100, 150, 255), (255, 200, 50), (50, 200, 200)]),
            "alpha": random.randint(60, 160)
        }

    def _build_menu(self):
        cx = self.screen_w // 2
        bw, bh, gap = 260, 54, 70
        start_y = 300
        self.menu_buttons = {
            "play":       Button(cx - bw//2, start_y,         bw, bh, "▶  Начать игру",      self.font_md),
            "highscores": Button(cx - bw//2, start_y + gap,   bw, bh, "🏆 Таблица рекордов", self.font_md),
            "help":       Button(cx - bw//2, start_y + 2*gap, bw, bh, "❓ Справка",           self.font_md),
            "quit":       Button(cx - bw//2, start_y + 3*gap, bw, bh, "✕  Выход",             self.font_md,
                                 (120, 40, 40), (180, 60, 60)),
        }

    def _build_mode_buttons(self):
        cx = self.screen_w // 2
        bw, bh = 280, 60
        self.mode_buttons = {
            "time":  Button(cx - bw//2, 280, bw, bh, "⏱  На время (2 мин)",  self.font_md),
            "score": Button(cx - bw//2, 360, bw, bh, "⭐ На очки (3 уровня)", self.font_md),
            "back":  Button(cx - bw//2, 480, bw, bh, "← Назад",               self.font_md,
                            (80, 40, 80), (120, 60, 120)),
        }

    def _back_button(self):
        return Button(30, 30, 120, 40, "← Назад", self.font_sm, (70, 35, 100), (110, 55, 150))

    def _start_game(self, mode):
        self.game_mode = mode
        self.score = 0
        self.combo = 0
        self.score_popups.clear()
        self.particles.particles.clear()
        if mode == "time":
            self.current_level = 0
            self.time_left = SETTINGS["game_modes"]["time_mode"]["time_limit"]
            level_cfg = LEVELS_CONFIG["levels"][0]
        else:
            self.current_level = 0
            level_cfg = LEVELS_CONFIG["levels"][self.current_level]
            self.level_target = level_cfg["target_score"]
            self.time_left = None
        self._init_board(level_cfg)
        self.state = self.PLAYING

    def _init_board(self, level_cfg):
        bcfg = SETTINGS["board"]
        self.board = Board(
            rows=bcfg["rows"],
            cols=bcfg["cols"],
            cell_size=bcfg["cell_size"],
            available_gems=level_cfg["available_gems"],
            special_chance=level_cfg.get("special_gems_chance", 0.08)
        )
        self.board_offset_x = bcfg["offset_x"]
        self.board_offset_y = bcfg["offset_y"]
        self.bg_color = tuple(level_cfg["background_color"])

    def _next_level(self):
        self.current_level += 1
        if self.current_level >= len(LEVELS_CONFIG["levels"]):
            self._end_game()
            return
        level_cfg = LEVELS_CONFIG["levels"][self.current_level]
        self.level_target = level_cfg["target_score"]
        self._init_board(level_cfg)
        self.sound.play("level_up")

    def _end_game(self):
        self.state = self.GAME_OVER
        if self.highscores.is_high_score(self.score):  # Проверяет попадание в ТОП-10
            self.sound.play("high_score")
            self.score_dialog.show(f"Ваш результат: {self.score} очков\nВведите имя:", with_input=True)
        else:
            self.sound.play("game_over")

    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.game_time += dt
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.score_dialog.visible:
                result = self.score_dialog.handle_event(event)
                if result == "confirm":
                    name = self.score_dialog.input_text.strip() or "Игрок"
                    mode_name = "На время" if self.game_mode == "time" else "На очки"
                    self.highscores.add(name, self.score, mode_name)
                return
            if self.state == self.MENU:
                self._handle_menu(event)
            elif self.state == self.MODE_SELECT:
                self._handle_mode_select(event)
            elif self.state == self.PLAYING:
                self._handle_playing(event)
            elif self.state in (self.HIGHSCORES, self.HELP, self.GAME_OVER):
                self._handle_back_screen(event)

    def _handle_menu(self, event):
        for name, btn in self.menu_buttons.items():
            if btn.handle_event(event):
                self.sound.play("menu_select")
                if name == "play":
                    self._build_mode_buttons()
                    self.state = self.MODE_SELECT
                elif name == "highscores":
                    self.state = self.HIGHSCORES
                elif name == "help":
                    self.state = self.HELP
                elif name == "quit":
                    self.running = False

    def _handle_mode_select(self, event):
        for name, btn in self.mode_buttons.items():
            if btn.handle_event(event):
                self.sound.play("menu_select")
                if name == "time":
                    self._start_game("time")
                elif name == "score":
                    self._start_game("score")
                elif name == "back":
                    self.state = self.MENU

    def _handle_playing(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self.MENU
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            bx = self.board_offset_x
            by = self.board_offset_y
            cs = SETTINGS["board"]["cell_size"]
            rows = SETTINGS["board"]["rows"]
            cols = SETTINGS["board"]["cols"]
            if bx <= mx < bx + cols * cs and by <= my < by + rows * cs:
                col = (mx - bx) // cs
                row = (my - by) // cs
                self.board.select(row, col)

    def _handle_back_screen(self, event):
        if not hasattr(self, '_back_btn'):
            self._back_btn = self._back_button()
        if self._back_btn.handle_event(event):
            self.sound.play("menu_select")
            self.state = self.MENU
            self._back_btn = None

    def _update(self, dt):
        self._update_bg_particles()
        if self.state == self.MENU:
            mouse = pygame.mouse.get_pos()
            for btn in self.menu_buttons.values():
                btn.update(mouse)
        elif self.state == self.MODE_SELECT:
            mouse = pygame.mouse.get_pos()
            for btn in self.mode_buttons.values():
                btn.update(mouse)
        elif self.state == self.PLAYING:
            self._update_game(dt)
        self.particles.update()
        self.score_popups = [p for p in self.score_popups if not p.is_dead()]
        for p in self.score_popups:
            p.update()
        if self.state in (self.HIGHSCORES, self.HELP, self.GAME_OVER):
            if not hasattr(self, '_back_btn') or not self._back_btn:
                self._back_btn = self._back_button()
            self._back_btn.update(pygame.mouse.get_pos())

    def _update_bg_particles(self):
        for p in self.bg_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -10 or p["x"] < -10 or p["x"] > self.screen_w + 10:
                p.update(self._new_bg_particle())

    def _update_game(self, dt):
        if not self.board:
            return
        if self.game_mode == "time" and self.time_left is not None:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self._end_game()
                return
        events = self.board.update(dt)
        if events["score"] > 0:
            self.score += events["score"]
            self.combo += 1
            if self.combo >= 3:
                self.sound.play("combo")
            else:
                self.sound.play("match")
            for eff in events.get("special_effects", []):
                snd = {"bomb": "bomb", "lightning": "lightning", "star": "star"}.get(eff["type"])
                if snd:
                    self.sound.play(snd)
            for (r, c) in events["matches"]:
                cx = self.board_offset_x + c * SETTINGS["board"]["cell_size"] + SETTINGS["board"]["cell_size"] // 2
                cy = self.board_offset_y + r * SETTINGS["board"]["cell_size"] + SETTINGS["board"]["cell_size"] // 2
                self.particles.emit(cx, cy, (200, 150, 255), 6)
            if events["matches"]:
                first_r, first_c = list(events["matches"])[0]
                px = self.board_offset_x + first_c * SETTINGS["board"]["cell_size"]
                py = self.board_offset_y + first_r * SETTINGS["board"]["cell_size"]
                self.score_popups.append(ScorePopup(px, py, events["score"], self.font_md))
        elif events["score"] == -1:
            self.sound.play("error")
            self.combo = 0
        if self.game_mode == "score" and self.score >= self.level_target:
            pygame.time.wait(500)
            self._next_level()
        if not self.board.swapping:
            if not self.board.has_possible_moves():
                self.board.shuffle()

    def _draw(self):
        if self.state == self.MENU:
            self._draw_menu()
        elif self.state == self.MODE_SELECT:
            self._draw_mode_select()
        elif self.state == self.PLAYING:
            self._draw_game()
        elif self.state == self.HIGHSCORES:
            self._draw_highscores()
        elif self.state == self.HELP:
            self._draw_help()
        elif self.state == self.GAME_OVER:
            self._draw_game_over()
        self.score_dialog.draw(self.screen)
        pygame.display.flip()

    def _draw_bg(self, color=(15, 5, 30)):
        self.screen.fill(color)
        for p in self.bg_particles:
            s = pygame.Surface((int(p["size"]*2+1), int(p["size"]*2+1)), pygame.SRCALPHA)
            c = p["color"] + (p["alpha"],)
            pygame.draw.circle(s, c, (int(p["size"]), int(p["size"])), int(p["size"]))
            self.screen.blit(s, (int(p["x"]), int(p["y"])))

    def _draw_menu(self):
        self._draw_bg()
        pulse = math.sin(self.game_time * 2) * 3
        title = self.font_xl.render("✦ Jewel Quest ✦", True, (255, 200, 80))
        subtitle = self.font_md.render("Магия драгоценных камней", True, (180, 130, 255))
        self.screen.blit(title, (self.screen_w//2 - title.get_width()//2, int(130 + pulse)))
        self.screen.blit(subtitle, (self.screen_w//2 - subtitle.get_width()//2, 210))
        gem_colors = list(GEM_COLORS.values())
        for i, color in enumerate(gem_colors[:7]):
            x = 60 + i * 100
            pygame.draw.circle(self.screen, color, (x, 250), 14)
        for btn in self.menu_buttons.values():
            btn.draw(self.screen)
        ver = self.font_sm.render("v1.0  |  Вариант 8", True, (100, 70, 140))
        self.screen.blit(ver, (self.screen_w - ver.get_width() - 15, self.screen_h - 30))

    def _draw_mode_select(self):
        self._draw_bg()
        title = self.font_lg.render("Выберите режим игры", True, (255, 200, 80))
        self.screen.blit(title, (self.screen_w//2 - title.get_width()//2, 170))
        descriptions = [
            ("⏱  На время:", "Набирайте очки за 2 минуты!", 290),
            ("⭐ На очки:",  "Пройдите 3 уровня с нарастающей сложностью", 370),
        ]
        for label, desc, y in descriptions:
            lbl = self.font_sm.render(label, True, (200, 160, 255))
            dsc = self.font_sm.render(desc, True, (160, 130, 200))
            self.screen.blit(lbl, (self.screen_w//2 - 130, y + 40))
            self.screen.blit(dsc, (self.screen_w//2 - 130, y + 60))
        for btn in self.mode_buttons.values():
            btn.draw(self.screen)

    def _draw_game(self):
        self.screen.fill(self.bg_color if hasattr(self, 'bg_color') else (15, 5, 30))
        if not self.board:
            return
        self.board.draw(self.screen, self.board_offset_x, self.board_offset_y, self.game_time)
        self.particles.draw(self.screen)
        for popup in self.score_popups:
            popup.draw(self.screen)
        self._draw_hud()

    def _draw_hud(self):
        hud_x = SETTINGS["board"]["offset_x"] + SETTINGS["board"]["cols"] * SETTINGS["board"]["cell_size"] + 20
        hud_y = SETTINGS["board"]["offset_y"]
        pygame.draw.rect(self.screen, (25, 10, 45), pygame.Rect(hud_x - 10, hud_y - 10, 180, 400), border_radius=12)
        pygame.draw.rect(self.screen, (80, 40, 120), pygame.Rect(hud_x - 10, hud_y - 10, 180, 400), 2, border_radius=12)
        score_label = self.font_sm.render("ОЧКИ", True, (150, 120, 200))
        score_val = self.font_lg.render(str(self.score), True, (255, 220, 80))
        self.screen.blit(score_label, (hud_x, hud_y + 10))
        self.screen.blit(score_val, (hud_x, hud_y + 30))
        if self.combo > 1:
            combo_col = (255, 150, 50) if self.combo < 5 else (255, 80, 50)
            combo_surf = self.font_md.render(f"×{self.combo} КОМБО!", True, combo_col)
            self.screen.blit(combo_surf, (hud_x, hud_y + 90))
        if self.game_mode == "time":
            t = max(0, int(self.time_left))
            col = (255, 80, 80) if t < 30 else (200, 200, 255)
            mode_label = self.font_sm.render("ВРЕМЯ", True, (150, 120, 200))
            time_val = self.font_lg.render(f"{t//60}:{t%60:02d}", True, col)
            self.screen.blit(mode_label, (hud_x, hud_y + 130))
            self.screen.blit(time_val, (hud_x, hud_y + 150))
            total_time = SETTINGS["game_modes"]["time_mode"]["time_limit"]
            bar_rect = pygame.Rect(hud_x, hud_y + 190, 150, 10)
            pygame.draw.rect(self.screen, (50, 30, 80), bar_rect, border_radius=5)
            fill = int(150 * self.time_left / total_time)
            if fill > 0:
                pygame.draw.rect(self.screen, col, pygame.Rect(hud_x, hud_y + 190, fill, 10), border_radius=5)
        else:
            level_cfg = LEVELS_CONFIG["levels"][self.current_level]
            lvl_label = self.font_sm.render(f"УРОВЕНЬ {self.current_level+1}", True, (150, 120, 200))
            lvl_name = self.font_sm.render(level_cfg["name"], True, (200, 180, 255))
            self.screen.blit(lvl_label, (hud_x, hud_y + 130))
            self.screen.blit(lvl_name, (hud_x, hud_y + 155))
            target = self.level_target
            progress = min(1.0, self.score / target)
            target_label = self.font_sm.render(f"Цель: {target}", True, (150, 120, 200))
            self.screen.blit(target_label, (hud_x, hud_y + 185))
            bar_rect = pygame.Rect(hud_x, hud_y + 210, 150, 10)
            pygame.draw.rect(self.screen, (50, 30, 80), bar_rect, border_radius=5)
            fill = int(150 * progress)
            if fill > 0:
                pygame.draw.rect(self.screen, (100, 220, 100), pygame.Rect(hud_x, hud_y + 210, fill, 10), border_radius=5)
        legend_y = hud_y + 240
        legend_title = self.font_sm.render("Спецкамни:", True, (180, 150, 230))
        self.screen.blit(legend_title, (hud_x, legend_y))
        specials = [((255, 80, 0), "💣 Бомба"), ((255, 255, 0), "⚡ Молния"), ((255, 215, 0), "⭐ Звезда")]
        for i, (color, name) in enumerate(specials):
            pygame.draw.circle(self.screen, color, (hud_x + 8, legend_y + 25 + i * 22), 6)
            lbl = self.font_sm.render(name, True, (180, 160, 220))
            self.screen.blit(lbl, (hud_x + 20, legend_y + 17 + i * 22))
        esc = self.font_sm.render("ESC — меню", True, (100, 80, 140))
        self.screen.blit(esc, (hud_x, hud_y + 370))

    def _draw_highscores(self):
        self._draw_bg()
        title = self.font_lg.render("🏆 Таблица рекордов", True, (255, 200, 80))
        self.screen.blit(title, (self.screen_w//2 - title.get_width()//2, 80))
        scores = self.highscores.get_top(10)
        if not scores:
            empty = self.font_md.render("Рекордов пока нет. Станьте первым!", True, (180, 150, 220))
            self.screen.blit(empty, (self.screen_w//2 - empty.get_width()//2, 300))
        else:
            headers = ["#", "Имя", "Очки", "Режим"]
            col_x = [80, 140, 380, 520]
            for i, h in enumerate(headers):
                s = self.font_sm.render(h, True, (150, 120, 200))
                self.screen.blit(s, (col_x[i], 150))
            pygame.draw.line(self.screen, (80, 50, 120), (60, 175), (self.screen_w - 60, 175), 1)
            for rank, entry in enumerate(scores, 1):
                y = 185 + (rank - 1) * 38
                color = (255, 215, 0) if rank == 1 else (200, 200, 200) if rank == 2 else (205, 127, 50) if rank == 3 else (160, 140, 200)
                for i, txt in enumerate([str(rank), entry["name"], str(entry["score"]), entry.get("mode", "—")]):
                    s = self.font_md.render(txt, True, color)
                    self.screen.blit(s, (col_x[i], y))
        if not hasattr(self, '_back_btn') or not self._back_btn:
            self._back_btn = self._back_button()
        self._back_btn.draw(self.screen)

    def _draw_help(self):
        self._draw_bg()
        title = self.font_lg.render("❓ Справка", True, (255, 200, 80))
        self.screen.blit(title, (self.screen_w//2 - title.get_width()//2, 50))
        help_lines = [
            ("ЦЕЛЬ ИГРЫ:", True),
            ("Меняйте местами соседние камни, чтобы создавать", False),
            ("линии из 3+ одинаковых камней.", False),
            ("", False),
            ("РЕЖИМЫ:", True),
            ("• На время — набирайте очки за 2 минуты", False),
            ("• На очки — пройдите 3 уровня с разными целями", False),
            ("", False),
            ("СПЕЦИАЛЬНЫЕ КАМНИ:", True),
            ("💣 Бомба — уничтожает все камни в радиусе 1 клетки", False),
            ("⚡ Молния — уничтожает целую строку и столбец", False),
            ("⭐ Звезда — уничтожает все камни своего цвета на доске", False),
            ("", False),
            ("ОЧКИ:", True),
            ("• 3 в ряд = 100 | 4 в ряд = 250 | 5+ в ряд = 500+", False),
            ("• Комбо увеличивает счётчик ×КОМБО", False),
            ("", False),
            ("Управление: мышь. ESC — выход в меню.", False),
        ]
        y = 130
        for line, is_header in help_lines:
            color = (255, 200, 80) if is_header else (190, 170, 220)
            font = self.font_md if is_header else self.font_sm
            surf = font.render(line, True, color)
            self.screen.blit(surf, (80, y))
            y += 28 if is_header else 24
        if not hasattr(self, '_back_btn') or not self._back_btn:
            self._back_btn = self._back_button()
        self._back_btn.draw(self.screen)

    def _draw_game_over(self):
        self._draw_bg((10, 5, 20))
        title_text = "🏆 Победа!" if self.game_mode == "score" else "⏱ Время вышло!"
        title = self.font_xl.render(title_text, True, (255, 200, 80))
        self.screen.blit(title, (self.screen_w//2 - title.get_width()//2, 160))
        score_surf = self.font_lg.render(f"Ваш результат: {self.score} очков", True, (220, 200, 255))
        self.screen.blit(score_surf, (self.screen_w//2 - score_surf.get_width()//2, 250))
        if self.highscores.is_high_score(self.score):
            hs = self.font_md.render("🎉 Это попадает в таблицу рекордов!", True, (255, 220, 80))
            self.screen.blit(hs, (self.screen_w//2 - hs.get_width()//2, 310))
        mode = "На время" if self.game_mode == "time" else "На очки"
        mode_surf = self.font_md.render(f"Режим: {mode}", True, (160, 140, 200))
        self.screen.blit(mode_surf, (self.screen_w//2 - mode_surf.get_width()//2, 360))
        if not hasattr(self, '_back_btn') or not self._back_btn:
            self._back_btn = self._back_button()
        self._back_btn.draw(self.screen)
