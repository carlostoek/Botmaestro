from .storage import USERS

ACHIEVEMENTS = {
    "first_points": {"name": "Primeros Puntos", "icon": "🌟"},
}


class AchievementService:
    """Simple achievement tracking."""

    def grant_achievement(self, user_id: int, achievement_id: str) -> bool:
        user = USERS.setdefault(user_id, {"points": 0, "level": 1, "achievements": set()})
        achievements = user.setdefault("achievements", set())
        if achievement_id not in achievements:
            achievements.add(achievement_id)
            return True
        return False

    def get_user_achievements(self, user_id: int) -> list[str]:
        return list(USERS.get(user_id, {}).get("achievements", set()))
