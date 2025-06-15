from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import bot, messages
from database import get_db
from services.subscription_service import list_active_subscriptions

router = Router()


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, command: Command.CommandObject) -> None:
    db = get_db()
    tg_user = message.from_user
    if tg_user is None:
        return

    # Only admins can broadcast
    async with db.execute("SELECT is_admin FROM user WHERE id=?", (tg_user.id,)) as cur:
        row = await cur.fetchone()
    if not (row and row["is_admin"] == 1):
        await message.answer(messages.ADMIN_ONLY)
        return

    text = command.args.strip() if command.args else None
    if not text:
        await message.answer(messages.BROADCAST_USAGE)
        return

    subs = await list_active_subscriptions()
    sent = 0
    for sub in subs:
        try:
            await bot.send_message(sub.user_id, text)
            sent += 1
        except Exception:
            # Ignore delivery errors (user blocked bot, etc.)
            pass

    await message.answer(messages.BROADCAST_SENT.format(count=sent))
