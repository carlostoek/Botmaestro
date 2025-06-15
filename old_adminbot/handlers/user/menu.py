from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

__all__ = ["USER_MENU_KB", "SUBSCRIPTION_MENU_KB"]

USER_MENU_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Mi perfil", callback_data="profile")],
        [InlineKeyboardButton(text="Ayuda", callback_data="help")],
        [InlineKeyboardButton(text="Estado de suscripción", callback_data="subscription_status")],
    ]
)

SUBSCRIPTION_MENU_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Suscribirme", callback_data="subscribe")],
        [InlineKeyboardButton(text="Ayuda", callback_data="help")],
    ]
)

