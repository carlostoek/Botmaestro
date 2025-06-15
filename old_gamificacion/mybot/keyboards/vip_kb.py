from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_vip_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="VIP Placeholder", callback_data="vip_placeholder")
    return builder.as_markup()
