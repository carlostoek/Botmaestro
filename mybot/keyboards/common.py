from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def get_back_kb(callback_data: str = "admin_back"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Volver", callback_data=callback_data)
    builder.adjust(1)
    return builder.as_markup()


def get_interactive_post_kb(message_id: int) -> InlineKeyboardMarkup:
    """Keyboard with Like/Share/Fire buttons for channel posts."""
    builder = InlineKeyboardBuilder()
    builder.button(text="👍 Me gusta", callback_data=f"ip_like_{message_id}")
    builder.button(text="🔁 Compartir", callback_data=f"ip_share_{message_id}")
    builder.button(text="🔥 Sexy", callback_data=f"ip_fire_{message_id}")
    builder.adjust(3)
    return builder.as_markup()
