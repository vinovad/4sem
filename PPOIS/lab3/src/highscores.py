import json
import os
from typing import List, Dict


SCORES_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "highscores.json")


class HighScores:
    MAX_ENTRIES = 10

    def __init__(self):
        self.scores: List[Dict] = []
        self.load()

    def load(self):
        try:
            with open(SCORES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.scores = data.get("scores", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.scores = []

    def save(self):
        os.makedirs(os.path.dirname(SCORES_PATH), exist_ok=True)
        with open(SCORES_PATH, "w", encoding="utf-8") as f:
            json.dump({"scores": self.scores}, f, ensure_ascii=False, indent=2)

    def add(self, name: str, score: int, mode: str) -> int:
        entry = {"name": name, "score": score, "mode": mode}
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:self.MAX_ENTRIES]
        self.save()
        return self.scores.index(entry) if entry in self.scores else -1

    def is_high_score(self, score: int) -> bool:
        if len(self.scores) < self.MAX_ENTRIES:
            return score > 0
        return score > self.scores[-1]["score"]

    def is_top_score(self, score: int) -> bool:
        if not self.scores:
            return score > 0
        return score > self.scores[0]["score"]

    def get_top(self, count: int = 10) -> List[Dict]:
        return self.scores[:count]
