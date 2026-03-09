import random
import json
import os
import pygame
from typing import List, Optional, Tuple, Set

from src.gem import Gem


class Board:
    def __init__(self, rows, cols, cell_size, available_gems, special_chance=0.08):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.available_gems = available_gems
        self.special_chance = special_chance
        self.grid: List[List[Optional[Gem]]] = []
        self.selected: Optional[Tuple[int, int]] = None
        self.matches: Set[Tuple[int, int]] = set()
        self.swapping = None
        self.swap_progress = 0.0
        self.swap_speed = 0.15
        self.swap_back = False
        self._fill()

    def _fill(self):
        self.grid = [[None] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                gem_type = self._pick_safe_type(r, c)
                gem = Gem(gem_type, r, c, self.cell_size)
                gem.scale = 1.0
                gem.is_appearing = False
                self.grid[r][c] = gem

    def _pick_safe_type(self, row, col):
        forbidden = set()
        if col >= 2:
            g1 = self.grid[row][col - 1]
            g2 = self.grid[row][col - 2]
            if g1 and g2 and g1.gem_type == g2.gem_type:
                forbidden.add(g1.gem_type)
        if row >= 2:
            g1 = self.grid[row - 1][col]
            g2 = self.grid[row - 2][col]
            if g1 and g2 and g1.gem_type == g2.gem_type:
                forbidden.add(g1.gem_type)
        choices = [t for t in self.available_gems if t not in forbidden]
        if not choices:
            choices = self.available_gems
        return random.choice(choices)

    def get_gem(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def select(self, row, col):
        if self.swapping:
            return None
        gem = self.get_gem(row, col)
        if not gem or gem.is_destroying or gem.is_appearing:
            return None
        if self.selected is None:
            self.selected = (row, col)
            gem.selected = True
            return "selected"
        sr, sc = self.selected
        prev_gem = self.get_gem(sr, sc)
        if (row, col) == (sr, sc):
            gem.selected = False
            self.selected = None
            return "deselect"
        if abs(row - sr) + abs(col - sc) == 1:
            if prev_gem:
                prev_gem.selected = False
            gem.selected = False
            self.selected = None
            self._start_swap((sr, sc), (row, col))
            return "swap"
        else:
            if prev_gem:
                prev_gem.selected = False
            self.selected = (row, col)
            gem.selected = True
            return "selected"

    def _start_swap(self, pos1, pos2):
        self.swapping = (pos1, pos2)
        self.swap_progress = 0.0
        self.swap_back = False

    def update(self, dt):
        events = {"matches": [], "score": 0, "combo": 0, "special_effects": []}
        for r in range(self.rows):
            for c in range(self.cols):
                gem = self.grid[r][c]
                if gem:
                    gem.update(dt)
        if self.swapping:
            self._update_swap(dt, events)
            return events
        destroying_count = sum(
            1 for r in range(self.rows) for c in range(self.cols)
            if self.grid[r][c] and self.grid[r][c].is_destroying
        )
        if destroying_count > 0:
            self._check_destroy_done()
            return events
        if self._apply_gravity():
            return events
        if self._fill_empty():
            return events
        matches = self.find_matches()
        if matches:
            score, special_effects = self._process_matches(matches)
            events["matches"] = list(matches)
            events["score"] = score
            events["special_effects"] = special_effects
        return events

    def _update_swap(self, dt, events):
        self.swap_progress = min(1.0, self.swap_progress + self.swap_speed)
        pos1, pos2 = self.swapping
        r1, c1 = pos1
        r2, c2 = pos2
        gem1 = self.grid[r1][c1]
        gem2 = self.grid[r2][c2]
        if not gem1 or not gem2:
            self.swapping = None
            return
        dx = (c2 - c1) * self.cell_size
        dy = (r2 - r1) * self.cell_size
        t = self._ease_in_out(self.swap_progress)
        if self.swap_back:
            t = 1.0 - t
        gem1.x = int(dx * t)
        gem1.y = int(dy * t)
        gem2.x = int(-dx * t)
        gem2.y = int(-dy * t)
        if self.swap_progress >= 1.0:
            gem1.x = gem1.y = gem2.x = gem2.y = 0
            if not self.swap_back:
                self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
                self.grid[r1][c1].row, self.grid[r1][c1].col = r1, c1
                self.grid[r2][c2].row, self.grid[r2][c2].col = r2, c2
                matches = self.find_matches()
                if not matches:
                    self.swap_back = True
                    self.swap_progress = 0.0
                    events["score"] = -1
                else:
                    self.swapping = None
            else:
                self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
                self.grid[r1][c1].row, self.grid[r1][c1].col = r1, c1
                self.grid[r2][c2].row, self.grid[r2][c2].col = r2, c2
                self.swapping = None

    def _ease_in_out(self, t):
        return t * t * (3 - 2 * t)

    def find_matches(self):
        matched = set()
        for r in range(self.rows):
            c = 0
            while c < self.cols - 2:
                gem = self.grid[r][c]
                if not gem or gem.is_destroying:
                    c += 1
                    continue
                streak = [c]
                nc = c + 1
                while nc < self.cols:
                    g2 = self.grid[r][nc]
                    if g2 and not g2.is_destroying and g2.gem_type == gem.gem_type:
                        streak.append(nc)
                        nc += 1
                    else:
                        break
                if len(streak) >= 3:
                    for col in streak:
                        matched.add((r, col))
                c = nc if len(streak) >= 3 else c + 1
        for c in range(self.cols):
            r = 0
            while r < self.rows - 2:
                gem = self.grid[r][c]
                if not gem or gem.is_destroying:
                    r += 1
                    continue
                streak = [r]
                nr = r + 1
                while nr < self.rows:
                    g2 = self.grid[nr][c]
                    if g2 and not g2.is_destroying and g2.gem_type == gem.gem_type:
                        streak.append(nr)
                        nr += 1
                    else:
                        break
                if len(streak) >= 3:
                    for row in streak:
                        matched.add((row, c))
                r = nr if len(streak) >= 3 else r + 1
        return matched

    def _process_matches(self, matches):
        score = 0
        special_effects = []
        for (r, c) in list(matches):
            gem = self.grid[r][c]
            if gem and gem.special != Gem.NORMAL:
                effect_cells = self._apply_special_effect(gem, r, c)
                special_effects.append({"type": gem.special, "cells": effect_cells, "row": r, "col": c})
                for er, ec in effect_cells:
                    if (er, ec) not in matches:
                        matches.add((er, ec))
                        g = self.grid[er][ec]
                        if g:
                            score += 50
        match_count = len(matches)
        if match_count <= 3:
            score += 100
        elif match_count <= 5:
            score += 250
        else:
            score += 500 + (match_count - 5) * 100
        for (r, c) in matches:
            gem = self.grid[r][c]
            if gem and not gem.is_destroying:
                gem.start_destroy()
        return score, special_effects

    def _apply_special_effect(self, gem, row, col):
        affected = []
        if gem.special == Gem.BOMB:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        affected.append((nr, nc))
        elif gem.special == Gem.LIGHTNING:
            for c in range(self.cols):
                affected.append((row, c))
            for r in range(self.rows):
                affected.append((r, col))
        elif gem.special == Gem.STAR:
            target_type = gem.gem_type
            for r in range(self.rows):
                for c in range(self.cols):
                    g = self.grid[r][c]
                    if g and g.gem_type == target_type:
                        affected.append((r, c))
        return list(set(affected))

    def _check_destroy_done(self):
        for r in range(self.rows):
            for c in range(self.cols):
                gem = self.grid[r][c]
                if gem and gem.is_dead():
                    self.grid[r][c] = None

    def _apply_gravity(self):
        moved = False
        for c in range(self.cols):
            for r in range(self.rows - 1, -1, -1):
                if self.grid[r][c] is None:
                    for nr in range(r - 1, -1, -1):
                        if self.grid[nr][c] is not None and not self.grid[nr][c].is_destroying:
                            gem = self.grid[nr][c]
                            self.grid[r][c] = gem
                            self.grid[nr][c] = None
                            gem.row = r
                            gem.col = c
                            gem.y = -(r - nr) * self.cell_size
                            moved = True
                            break
        fall_speed = 14
        any_falling = False
        for r in range(self.rows):
            for c in range(self.cols):
                gem = self.grid[r][c]
                if gem and gem.y < 0:
                    gem.y = min(0, gem.y + fall_speed)
                    any_falling = True
        return any_falling or moved

    def _fill_empty(self):
        added = False
        for c in range(self.cols):
            for r in range(self.rows):
                if self.grid[r][c] is None:
                    gem_type = random.choice(self.available_gems)
                    special = Gem.NORMAL
                    if random.random() < self.special_chance:
                        special = random.choice([Gem.BOMB, Gem.LIGHTNING, Gem.STAR])
                    gem = Gem(gem_type, r, c, self.cell_size, special)
                    gem.y = -(r + 1) * self.cell_size
                    self.grid[r][c] = gem
                    added = True
        return added

    def has_possible_moves(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if c + 1 < self.cols:
                    self._do_swap(r, c, r, c + 1)
                    if self.find_matches():
                        self._do_swap(r, c, r, c + 1)
                        return True
                    self._do_swap(r, c, r, c + 1)
                if r + 1 < self.rows:
                    self._do_swap(r, c, r + 1, c)
                    if self.find_matches():
                        self._do_swap(r, c, r + 1, c)
                        return True
                    self._do_swap(r, c, r + 1, c)
        return False

    def _do_swap(self, r1, c1, r2, c2):
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        if self.grid[r1][c1]:
            self.grid[r1][c1].row, self.grid[r1][c1].col = r1, c1
        if self.grid[r2][c2]:
            self.grid[r2][c2].row, self.grid[r2][c2].col = r2, c2

    def shuffle(self):
        gems = [self.grid[r][c] for r in range(self.rows) for c in range(self.cols) if self.grid[r][c]]
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        random.shuffle(positions)
        for i, (r, c) in enumerate(positions):
            if i < len(gems):
                gem = gems[i]
                gem.row, gem.col = r, c
                self.grid[r][c] = gem
                gem.scale = 0.0
                gem.is_appearing = True

    def draw(self, surface, offset_x, offset_y, time):
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(
                    offset_x + c * self.cell_size,
                    offset_y + r * self.cell_size,
                    self.cell_size, self.cell_size
                )
                color = (40, 20, 60) if (r + c) % 2 == 0 else (50, 25, 75)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (80, 40, 120), rect, 1)
        for r in range(self.rows):
            for c in range(self.cols):
                gem = self.grid[r][c]
                if gem:
                    gem.draw(surface, offset_x, offset_y, self.cell_size, time)
