from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from utils.config import DEFAULT_REACTION_BUTTONS


def get_back_kb(callback_data: str = "admin_back"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Volver", callback_data=callback_data)
    builder.adjust(1)
    return builder.as_markup()


def get_interactive_post_kb(
    message_id: int, buttons: list[str] | None = None
) -> InlineKeyboardMarkup:
    """Keyboard with reaction buttons for channel posts."""
    texts = (
        buttons if buttons and len(buttons) >= 3 else DEFAULT_REACTION_BUTTONS
    )
    builder = InlineKeyboardBuilder()
    builder.button(text=texts[0], callback_data=f"ip_like_{message_id}")
    builder.button(text=texts[1], callback_data=f"ip_share_{message_id}")
    builder.button(text=texts[2], callback_data=f"ip_fire_{message_id}")
    builder.adjust(3)
    return builder.as_markup()
