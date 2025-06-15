from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_game_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Mi perfil", callback_data="game_profile")
    builder.button(text="Ganar puntos", callback_data="gain_points")
    return builder.as_markup()
