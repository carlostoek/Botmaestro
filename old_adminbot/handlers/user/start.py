from __future__ import annotations

import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from handlers.user.menu import USER_MENU_KB, SUBSCRIPTION_MENU_KB
from handlers.admin.menu import ADMIN_MENU_KB

from database import get_db
from services.subscription_service import add_subscription, get_subscription
from services.token_service import validate_token, mark_token_as_used
from bot import messages

router = Router()

FAKE_INVITE_LINK = "https://t.me/+fake_invite"  # placeholder


@router.message(Command("start"))
async def cmd_start(message: Message, command: Command.CommandObject) -> None:
    db = get_db()

    tg_user = message.from_user
    if tg_user is None:
        return

    # Ensure user exists in DB
    await db.execute(
        "INSERT OR IGNORE INTO user (id, username, full_name) VALUES (?, ?, ?)",
        (tg_user.id, tg_user.username or "", tg_user.full_name or ""),
    )
    await db.commit()

    token = command.args.strip() if command.args else None
    if token:
        duration = await validate_token(token)
        if duration is None:
            await message.answer(messages.INVALID_TOKEN)
            return
        await mark_token_as_used(token)
        await add_subscription(tg_user.id, duration)
        await message.answer(
            messages.SUB_ACTIVATED_WITH_LINK.format(
                duration=duration, invite=FAKE_INVITE_LINK
            )
        )
        return

    # Determine role and show menu
    async with db.execute("SELECT is_admin FROM user WHERE id=?", (tg_user.id,)) as cur:
        row = await cur.fetchone()
    is_admin = row and row["is_admin"] == 1

    sub = await get_subscription(tg_user.id)
    active = sub and sub.end_date > datetime.datetime.utcnow()

    if is_admin:
        await message.answer(messages.ADMIN_MENU, reply_markup=ADMIN_MENU_KB)
    elif active:
        await message.answer(messages.SUBSCRIBER_MENU, reply_markup=USER_MENU_KB)
    else:
        await message.answer(
            messages.SUBSCRIPTION_MENU,
            reply_markup=SUBSCRIPTION_MENU_KB,
        )
