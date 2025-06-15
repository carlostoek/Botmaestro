from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import set_user_menu_state


async def send_menu(message: Message, text: str, reply_markup, session: AsyncSession, state: str) -> None:
    """Send a new menu message and store the user's state."""
    await message.answer(text, reply_markup=reply_markup)
    await set_user_menu_state(session, message.from_user.id, state)


async def update_menu(callback: CallbackQuery, text: str, reply_markup, session: AsyncSession, state: str) -> None:
    """Edit the current menu message and update the user's state."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc).lower():
            raise
    await set_user_menu_state(session, callback.from_user.id, state)
