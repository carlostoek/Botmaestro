from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_vip_game_menu_kb():
    """Keyboard for the VIP game menu."""
    builder = InlineKeyboardBuilder()
    builder.button(text="\U0001F4CA Perfil", callback_data="vip_profile")
    builder.button(text="\U0001F381 Obtener Puntos", callback_data="vip_gain_points")
    return builder.as_markup()


def get_vip_profile_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="\u2b05\ufe0f Volver", callback_data="vip_game_menu")
    return builder.as_markup()
