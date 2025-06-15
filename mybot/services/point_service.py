from .storage import USERS


class PointService:
    """Manage user points in memory."""

    def add_points(self, user_id: int, points: int) -> dict:
        user = USERS.setdefault(user_id, {"points": 0, "level": 1, "achievements": set()})
        user["points"] += points
        return user

    def get_user_points(self, user_id: int) -> int:
        return USERS.get(user_id, {}).get("points", 0)

    def get_top_users(self, limit: int = 10) -> list[tuple[int, int]]:
        ranking = sorted(((uid, data["points"]) for uid, data in USERS.items()),
                         key=lambda x: x[1], reverse=True)
        return ranking[:limit]
