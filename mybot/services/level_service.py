from .storage import USERS

# Simple level thresholds
LEVEL_THRESHOLDS = {1: 0, 2: 10, 3: 25, 4: 50, 5: 100}


class LevelService:
    """Handle level progression."""

    def check_for_level_up(self, user: dict) -> bool:
        leveled_up = False
        while True:
            next_level = user["level"] + 1
            threshold = LEVEL_THRESHOLDS.get(next_level)
            if threshold is None:
                break
            if user["points"] >= threshold:
                user["level"] = next_level
                leveled_up = True
            else:
                break
        return leveled_up

    def get_user_level(self, user_id: int) -> int:
        return USERS.get(user_id, {}).get("level", 1)
