from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_kb():
    """Return a minimal free-user menu."""

    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Minijuego Kinky", callback_data="free_game")
    builder.button(text="ℹ️ Información", callback_data="free_info")
    builder.adjust(1)
    return builder.as_markup()
