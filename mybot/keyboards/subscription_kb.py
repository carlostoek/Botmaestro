from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_kb():
    """Return a minimal free-user menu."""

    builder = InlineKeyboardBuilder()
    # Button to request access or interact in the free channel
    builder.button(text="Botón de suscriptor free", callback_data="free_button")
    # Simplified game available for free users
    builder.button(text="🎮 Juego del Diván Lite", callback_data="free_game")
    builder.adjust(1)
    return builder.as_markup()
