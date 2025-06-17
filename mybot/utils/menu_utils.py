from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import set_user_menu_state
from utils.user_roles import (
    ADMIN_ROLE,
    VIP_ROLE,
    FREE_ROLE,
    get_user_role,
)
from keyboards.admin_main_kb import get_admin_main_kb
from keyboards.vip_main_kb import get_vip_main_kb
from keyboards.subscription_kb import get_subscription_kb

# Cache to store the latest menu message for each user
MENU_CACHE: dict[int, tuple[int, int]] = {}
# Cache to track the most recent non-menu message for each user
GENERAL_CACHE: dict[int, tuple[int, int]] = {}


async def _delete_general(bot, user_id: int) -> None:
    """Delete the user's previous non-menu message if it exists."""
    prev = GENERAL_CACHE.pop(user_id, None)
    if prev:
        chat_id, msg_id = prev
        try:
            await bot.delete_message(chat_id, msg_id)
        except TelegramBadRequest:
            pass


async def send_menu(
    message: Message,
    text: str,
    reply_markup,
    session: AsyncSession,
    state: str,
) -> None:
    """Send or update a menu ensuring a single message per user."""
    user_id = message.from_user.id
    bot = message.bot
    await _delete_general(bot, user_id)
    prev = MENU_CACHE.get(user_id)
    if prev:
        chat_id, msg_id = prev
        try:
            await bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=reply_markup,
            )
            await set_user_menu_state(session, user_id, state)
            return
        except TelegramBadRequest:
            try:
                await bot.delete_message(chat_id, msg_id)
            except TelegramBadRequest:
                pass

    sent = await message.answer(text, reply_markup=reply_markup)
    MENU_CACHE[user_id] = (sent.chat.id, sent.message_id)
    await set_user_menu_state(session, user_id, state)


async def update_menu(
    callback: CallbackQuery,
    text: str,
    reply_markup,
    session: AsyncSession,
    state: str,
) -> None:
    """Edit the previous menu message or send a new one."""
    user_id = callback.from_user.id
    bot = callback.bot
    msg = callback.message
    await _delete_general(bot, user_id)
    try:
        await msg.edit_text(text, reply_markup=reply_markup)
        MENU_CACHE[user_id] = (msg.chat.id, msg.message_id)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc).lower():
            pass
        else:
            try:
                await bot.delete_message(msg.chat.id, msg.message_id)
            except TelegramBadRequest:
                pass
            new_msg = await bot.send_message(msg.chat.id, text, reply_markup=reply_markup)
            MENU_CACHE[user_id] = (new_msg.chat.id, new_msg.message_id)
    await set_user_menu_state(session, user_id, state)


async def send_temporary_reply(
    message: Message,
    text: str,
    reply_markup=None,
    delay: int = 5,
) -> None:
    """Send a message that auto-deletes after ``delay`` seconds."""
    user_id = message.from_user.id
    bot = message.bot
    await _delete_general(bot, user_id)
    sent = await message.answer(text, reply_markup=reply_markup)
    GENERAL_CACHE[user_id] = (sent.chat.id, sent.message_id)
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(sent.chat.id, sent.message_id)
    except TelegramBadRequest:
        pass
    if GENERAL_CACHE.get(user_id) == (sent.chat.id, sent.message_id):
        GENERAL_CACHE.pop(user_id, None)


async def send_clean_message(
    message: Message,
    text: str,
    reply_markup=None,
) -> Message:
    """Send a message after removing the previous one for this user."""
    user_id = message.from_user.id
    bot = message.bot
    await _delete_general(bot, user_id)
    sent = await message.answer(text, reply_markup=reply_markup)
    GENERAL_CACHE[user_id] = (sent.chat.id, sent.message_id)
    return sent


async def send_role_menu(message: Message, session: AsyncSession) -> None:
    """Display the appropriate main menu based on the user's role."""
    user_id = message.from_user.id
    bot = message.bot

    role = await get_user_role(bot, user_id, session=session)

    if role == ADMIN_ROLE:
        text = "Panel de Administración"
        markup = get_admin_main_kb()
        state = "admin_main"
    elif role == VIP_ROLE:
        text = "Bienvenido al Diván de Diana"
        markup = get_vip_main_kb()
        state = "vip_main"
    else:  # FREE_ROLE
        text = "Bienvenido a los Kinkys"
        markup = get_subscription_kb()
        state = "free_main"

    await send_menu(message, text, markup, session, state)
