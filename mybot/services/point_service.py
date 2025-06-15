"""In-memory point tracking service."""

from typing import Dict

_user_points: Dict[int, int] = {}


def add_points(user_id: int, points: int) -> int:
    """Add points to a user and return new total."""
    current = _user_points.get(user_id, 0) + points
    _user_points[user_id] = current
    return current


def get_user_points(user_id: int) -> int:
    """Return user points."""
    return _user_points.get(user_id, 0)
