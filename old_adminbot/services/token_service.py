import secrets
from typing import Optional

from database import get_db

__all__ = [
    "generate_token",
    "validate_token",
    "mark_token_as_used",
]


async def generate_token(duration_days: int) -> str:
    """Generate a unique token and store it in the database."""
    db = get_db()
    while True:
        token = secrets.token_urlsafe(8)
        try:
            await db.execute(
                "INSERT INTO token (token, duration_days, used) VALUES (?, ?, 0)",
                (token, duration_days),
            )
            await db.commit()
            return token
        except Exception as exc:  # aiosqlite.IntegrityError if token already exists
            # Retry with a new token if duplicate
            if type(exc).__name__ == "IntegrityError":
                continue
            raise


async def validate_token(token: str) -> Optional[int]:
    """Return the duration if the token exists and hasn't been used."""
    db = get_db()
    async with db.execute(
        "SELECT duration_days, used FROM token WHERE token=?", (token,)
    ) as cursor:
        row = await cursor.fetchone()
    if row is None or row["used"]:
        return None
    return int(row["duration_days"])


async def mark_token_as_used(token: str) -> None:
    """Mark a token as used."""
    db = get_db()
    await db.execute("UPDATE token SET used=1 WHERE token=?", (token,))
    await db.commit()
