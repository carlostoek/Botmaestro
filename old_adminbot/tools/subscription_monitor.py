import asyncio
import datetime

from aiogram.exceptions import TelegramAPIError

from bot import bot, messages
from database import get_db
from services.subscription_service import remove_subscription
from services.config_service import get_config


async def _check_subscriptions() -> None:
    """Check all subscriptions and notify users or remove access."""
    db = get_db()
    now = datetime.datetime.utcnow()
    tomorrow = now + datetime.timedelta(days=1)
    reminder_msg = await get_config("reminder_msg") or messages.DEFAULT_REMINDER_MSG
    expiration_msg = (
        await get_config("expiration_msg") or messages.DEFAULT_EXPIRATION_MSG
    )
    async with db.execute("SELECT user_id, end_date FROM subscription") as cursor:
        rows = await cursor.fetchall()

    for row in rows:
        user_id = int(row["user_id"])
        end_date = datetime.datetime.fromisoformat(row["end_date"])

        if now < end_date <= tomorrow:
            # Notify user subscription expires in one day
            try:
                await bot.send_message(user_id, reminder_msg)
            except TelegramAPIError:
                pass
        elif end_date <= now:
            await remove_subscription(user_id)
            try:
                await bot.send_message(user_id, expiration_msg)
            except TelegramAPIError:
                pass


async def monitor_subscriptions() -> None:
    """Background task that runs once every 24 hours."""
    while True:
        await _check_subscriptions()
        await asyncio.sleep(24 * 60 * 60)


