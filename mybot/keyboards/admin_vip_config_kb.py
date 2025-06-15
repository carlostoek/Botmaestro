from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_vip_config_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 Tarifas", callback_data="config_tarifas")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(1)
    return builder.as_markup()
