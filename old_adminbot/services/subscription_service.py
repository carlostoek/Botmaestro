import datetime
from typing import List, Optional

from database import get_db
from database.models import Subscription

__all__ = [
    "add_subscription",
    "get_subscription",
    "remove_subscription",
    "list_active_subscriptions",
]


async def add_subscription(user_id: int, duration_days: int) -> None:
    """Add or extend a user's subscription."""
    db = get_db()
    now = datetime.datetime.utcnow()
    async with db.execute(
        "SELECT start_date, end_date FROM subscription WHERE user_id=?",
        (user_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if row:
        start = datetime.datetime.fromisoformat(row["start_date"])
        end = datetime.datetime.fromisoformat(row["end_date"])
        if end < now:
            start = now
            end = now + datetime.timedelta(days=duration_days)
        else:
            end = end + datetime.timedelta(days=duration_days)
        await db.execute(
            "UPDATE subscription SET start_date=?, end_date=? WHERE user_id=?",
            (start.isoformat(), end.isoformat(), user_id),
        )
    else:
        start = now
        end = now + datetime.timedelta(days=duration_days)
        await db.execute(
            "INSERT INTO subscription (user_id, start_date, end_date) VALUES (?, ?, ?)",
            (user_id, start.isoformat(), end.isoformat()),
        )
    await db.commit()


async def get_subscription(user_id: int) -> Optional[Subscription]:
    """Return the subscription for the given user if it exists."""
    db = get_db()
    async with db.execute(
        "SELECT user_id, start_date, end_date FROM subscription WHERE user_id=?",
        (user_id,),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        return None
    return Subscription(
        user_id=row["user_id"],
        start_date=datetime.datetime.fromisoformat(row["start_date"]),
        end_date=datetime.datetime.fromisoformat(row["end_date"]),
    )


async def remove_subscription(user_id: int) -> None:
    """Remove a user's subscription."""
    db = get_db()
    await db.execute("DELETE FROM subscription WHERE user_id=?", (user_id,))
    await db.commit()


async def list_active_subscriptions() -> List[Subscription]:
    """Return a list of currently active subscriptions."""
    db = get_db()
    now = datetime.datetime.utcnow().isoformat()
    async with db.execute(
        "SELECT user_id, start_date, end_date FROM subscription WHERE end_date>?",
        (now,),
    ) as cursor:
        rows = await cursor.fetchall()
    return [
        Subscription(
            user_id=row["user_id"],
            start_date=datetime.datetime.fromisoformat(row["start_date"]),
            end_date=datetime.datetime.fromisoformat(row["end_date"]),
        )
        for row in rows
    ]
