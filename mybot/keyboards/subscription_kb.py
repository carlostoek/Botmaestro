from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Request Access", callback_data="request_access")
    return builder.as_markup()
