from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_config_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Configurar Reacciones", callback_data="config_reaction_buttons")
    builder.button(text="🔙 Volver", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()
