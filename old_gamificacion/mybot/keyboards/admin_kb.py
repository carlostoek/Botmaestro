from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Admin Placeholder", callback_data="admin_placeholder")
    return builder.as_markup()
