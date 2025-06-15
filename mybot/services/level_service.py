"""Simple level calculation service."""

from typing import Dict
from .point_service import get_user_points

# Cumulative points needed to reach each level
LEVEL_THRESHOLDS = {
    1: 0,
    2: 10,
    3: 25,
    4: 50,
    5: 100,
    6: 200,
    7: 350,
    8: 550,
    9: 800,
    10: 1100,
}

_user_levels: Dict[int, int] = {}


def get_user_level(user_id: int) -> int:
    return _user_levels.get(user_id, 1)


def check_for_level_up(user_id: int) -> tuple[bool, int]:
    """Check and apply level ups. Returns (leveled_up, new_level)."""
    points = get_user_points(user_id)
    level = _user_levels.get(user_id, 1)
    leveled_up = False
    while points >= LEVEL_THRESHOLDS.get(level + 1, float("inf")):
        level += 1
        leveled_up = True
    _user_levels[user_id] = level
    return leveled_up, level
