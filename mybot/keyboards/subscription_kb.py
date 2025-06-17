from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_kb():
    """Return the menu keyboard for free users."""

    builder = InlineKeyboardBuilder()
    builder.button(text="Información", callback_data="free_info")
    builder.button(text="Minijuego Kinky", callback_data="free_game")
    builder.adjust(1)
    return builder.as_markup()


def get_free_info_kb():
    """Keyboard shown in the information section."""

    builder = InlineKeyboardBuilder()
    builder.button(text="Botón de prueba", callback_data="free_info_test")
    builder.adjust(1)
    return builder.as_markup()


def get_free_game_kb():
    """Keyboard shown in the free mini game section."""

    builder = InlineKeyboardBuilder()
    builder.button(text="Botón de prueba", callback_data="free_game_test")
    builder.adjust(1)
    return builder.as_markup()
