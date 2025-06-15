"""Minimal achievement tracking."""

from typing import Dict, Set

ACHIEVEMENTS = {
    "first_points": "Primeros Puntos"
}

_user_achievements: Dict[int, Set[str]] = {}


def grant_achievement(user_id: int, achievement_id: str) -> bool:
    achievements = _user_achievements.setdefault(user_id, set())
    if achievement_id in achievements:
        return False
    achievements.add(achievement_id)
    return True


def get_user_achievements(user_id: int) -> Set[str]:
    return _user_achievements.get(user_id, set())
