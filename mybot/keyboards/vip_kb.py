from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_vip_kb():
    """Return a minimal VIP subscriber menu."""

    builder = InlineKeyboardBuilder()
    # Single button for VIP subscribers
    builder.button(text="Botón de suscriptor VIP", callback_data="vip_button")
    return builder.as_markup()
