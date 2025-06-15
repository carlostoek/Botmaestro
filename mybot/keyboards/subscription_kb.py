from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_kb():
    """Return a minimal free-user menu."""

    builder = InlineKeyboardBuilder()
    # Single button for free channel subscribers or access requests
    builder.button(text="Botón de suscriptor free", callback_data="free_button")
    return builder.as_markup()
