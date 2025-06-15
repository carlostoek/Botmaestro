from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_config_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Tarifas", callback_data="config_plans")
    builder.button(text="🔙 Volver", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()
