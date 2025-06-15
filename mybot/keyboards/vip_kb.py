from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_vip_kb():
    """Keyboard for regular VIP users."""

    builder = InlineKeyboardBuilder()
    builder.button(text="🧾 Mi Suscripción", callback_data="vip_subscription")
    builder.button(text="🎮 Juego del Diván", callback_data="vip_game")
    builder.adjust(1)
    return builder.as_markup()
