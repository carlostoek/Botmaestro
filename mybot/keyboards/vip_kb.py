from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_vip_kb():
    """Return the VIP user menu keyboard."""

    builder = InlineKeyboardBuilder()
    builder.button(text="🧾 Mi Suscripción", callback_data="vip_subscription")
    builder.button(text="🎮 Juego del Diván", callback_data="menu_principal")
    builder.adjust(1)
    return builder.as_markup()
