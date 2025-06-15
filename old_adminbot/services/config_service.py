from typing import Optional

from database import get_db

__all__ = [
    "get_config",
    "set_config",
    "get_pricing",
    "set_pricing",
    "get_price",
    "set_price",
]


async def get_config(key: str) -> Optional[str]:
    """Return the configuration value for the given key."""
    db = get_db()
    async with db.execute("SELECT value FROM config WHERE key=?", (key,)) as cur:
        row = await cur.fetchone()
    if row is None:
        return None
    return str(row["value"])


async def set_config(key: str, value: str) -> None:
    """Set a configuration value."""
    db = get_db()
    await db.execute(
        "INSERT INTO config (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    await db.commit()

async def get_pricing() -> Optional[tuple[str, str]]:
    period = await get_config("price_period")
    amount = await get_config("price_amount")
    if period is None or amount is None:
        return None
    return period, amount


async def set_pricing(period: str, amount: str) -> None:
    await set_config("price_period", period)
    await set_config("price_amount", amount)


async def set_price(period: str, amount: str) -> None:
    """Store price for a specific subscription period."""
    await set_config(f"price_{period}", amount)


async def get_price(period: str) -> Optional[str]:
    """Return the price for the given subscription period if set."""
    return await get_config(f"price_{period}")

