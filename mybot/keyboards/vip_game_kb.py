from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_game_menu_kb(include_back: bool = False):
    """Keyboard for the Juego del Diván main menu."""
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Perfil", callback_data="game_profile")
    builder.button(text="Ganar puntos", callback_data="gain_points")
    if include_back:
        builder.button(text="🔙 Volver", callback_data="game_back")
    builder.adjust(1)
    return builder.as_markup()


def get_profile_kb():
    """Keyboard for the profile screen inside the game."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Volver", callback_data="game_menu")
    builder.adjust(1)
    return builder.as_markup()
