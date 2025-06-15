from __future__ import annotations

from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

import datetime
from zoneinfo import ZoneInfo

from services.config_service import get_pricing, get_config, set_price
from services.subscription_service import list_active_subscriptions, remove_subscription
from services.token_service import generate_token
from bot import messages
from config import settings
from database import get_db

router = Router()
__all__ = ["ADMIN_MENU_KB", "router"]

# Temporary storage for admins currently setting a price
_waiting_price: dict[int, str] = {}

ADMIN_MENU_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Ajustes", callback_data="admin_settings")],
        [InlineKeyboardButton(text="🛠️ Administración", callback_data="admin_tools")],
    ]
)

SETTINGS_MENU_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Definir precio", callback_data="settings_set_price")],
        [InlineKeyboardButton(text="Volver", callback_data="back_admin_menu")],
    ]
)

PRICE_PERIOD_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1 día", callback_data="price_period:1d")],
        [InlineKeyboardButton(text="1 semana", callback_data="price_period:1w")],
        [InlineKeyboardButton(text="2 semanas", callback_data="price_period:2w")],
        [InlineKeyboardButton(text="1 mes", callback_data="price_period:1m")],
        [InlineKeyboardButton(text="Permanente", callback_data="price_period:perm")],
        [InlineKeyboardButton(text="Volver", callback_data="admin_settings")],
    ]
)

ADMINISTRATION_MENU_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="\U0001F4C8 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton(text="Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="Generar enlace", callback_data="admin_gen_link")],
        [InlineKeyboardButton(text="Suscriptores", callback_data="admin_list_subs")],
        [InlineKeyboardButton(text="Volver", callback_data="back_admin_menu")],
    ]
)


@router.callback_query(lambda c: c.data == "admin_settings")
async def cb_settings(callback: CallbackQuery) -> None:
    pricing = await get_pricing()
    text = messages.SETTINGS_MENU
    if pricing:
        text += "\n" + messages.CURRENT_PRICE.format(period=pricing[0], amount=pricing[1])
    await callback.message.edit_text(text, reply_markup=SETTINGS_MENU_KB)
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings_set_price")
async def cb_set_price(callback: CallbackQuery) -> None:
    await callback.message.edit_text(messages.PRICE_SELECT_PERIOD, reply_markup=PRICE_PERIOD_KB)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("price_period:"))
async def cb_price_period(callback: CallbackQuery) -> None:
    period = callback.data.split(":", 1)[1]
    tg_id = callback.from_user.id if callback.from_user else None
    if tg_id is None:
        await callback.answer()
        return
    _waiting_price[tg_id] = period
    await callback.message.edit_text(messages.PRICE_ENTER_AMOUNT)
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_tools")
async def cb_tools(callback: CallbackQuery) -> None:
    await callback.message.edit_text(messages.ADMINISTRATION_MENU, reply_markup=ADMINISTRATION_MENU_KB)
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_admin_menu")
async def cb_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text(messages.ADMIN_MENU, reply_markup=ADMIN_MENU_KB)
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_stats")
async def cb_stats(callback: CallbackQuery) -> None:
    db = get_db()
    now_iso = datetime.datetime.utcnow().isoformat()

    async with db.execute("SELECT COUNT(*) FROM user") as cur:
        row = await cur.fetchone()
    total_users = int(row[0]) if row else 0

    subs = await list_active_subscriptions()
    active = len(subs)

    async with db.execute(
        "SELECT COUNT(*) FROM subscription WHERE end_date<=?", (now_iso,)
    ) as cur:
        row = await cur.fetchone()
    expired = int(row[0]) if row else 0

    async with db.execute("SELECT COUNT(*) FROM token WHERE used=1") as cur:
        row = await cur.fetchone()
    renewals = int(row[0]) if row else 0

    async with db.execute(
        "SELECT duration_days, COUNT(*) c FROM token WHERE used=1 GROUP BY duration_days ORDER BY c DESC LIMIT 1"
    ) as cur:
        row = await cur.fetchone()
    if row:
        days = int(row[0])
        if days >= 365 * 5:
            period = "permanent"
        elif days % 30 == 0:
            m = days // 30
            period = f"{m} month{'s' if m != 1 else ''}"
        else:
            period = f"{days} day{'s' if days != 1 else ''}"
    else:
        period = "N/A"

    pricing = await get_pricing()
    amount = float(pricing[1]) if pricing else 0
    revenue = active * amount

    currency = await get_config("currency") or "USD"
    tz_name = await get_config("timezone") or "UTC"
    try:
        local_time = datetime.datetime.now(ZoneInfo(tz_name)).strftime("%I:%M %p")
    except Exception:
        local_time = datetime.datetime.utcnow().strftime("%I:%M %p")
        tz_name = "UTC"

    text = messages.BOLD_STATS.format(
        total=total_users,
        active=active,
        expired=expired,
        renewals=renewals,
        period=period,
        revenue=f"{revenue:,.0f}",
        currency=currency,
        time=local_time,
        tz=tz_name,
    )

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_broadcast")
async def cb_broadcast(callback: CallbackQuery) -> None:
    await callback.message.answer(messages.BROADCAST_INSTRUCTIONS)
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_gen_link")
async def cb_gen_link(callback: CallbackQuery) -> None:
    token = await generate_token(7)
    link = f"https://t.me/{settings.BOT_TOKEN.split(':')[0]}?start={token}"
    await callback.message.answer(messages.ACCESS_LINK.format(link=link))
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_list_subs")
async def cb_list_subs(callback: CallbackQuery) -> None:
    subs = await list_active_subscriptions()
    for sub in subs:
        days = (sub.end_date - sub.start_date).days
        text = messages.SUBSCRIBER_INFO.format(
            user_id=sub.user_id,
            start=sub.start_date.date(),
            end=sub.end_date.date(),
            days=days,
            renewals=0,
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Eliminar", callback_data=f"remove_user:{sub.user_id}")]]
        )
        await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("remove_user:"))
async def cb_remove(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split(":", 1)[1])
    await remove_subscription(user_id)
    await callback.message.answer(messages.USER_REMOVED.format(user_id=user_id))
    await callback.answer()


@router.message(lambda m: m.from_user and m.from_user.id in _waiting_price)
async def price_input(message: Message) -> None:
    tg_id = message.from_user.id
    period = _waiting_price.get(tg_id)
    if period is None:
        return
    amount = message.text.strip()
    if not amount.isdigit():
        await message.answer(messages.PRICE_ENTER_AMOUNT)
        return
    del _waiting_price[tg_id]
    await set_price(period, amount)
    await message.answer(messages.PRICE_UPDATED.format(period=period, amount=amount))

