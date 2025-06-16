from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_config_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Configurar Reacciones", callback_data="config_reaction_buttons")
    builder.button(text="➕ Agregar canales", callback_data="config_add_channels")
    builder.button(text="⏱️ Schedulers", callback_data="config_scheduler")
    builder.button(text="🔙 Volver", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()


def get_scheduler_config_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="⏲ Intervalo Canal", callback_data="set_channel_interval")
    builder.button(text="⏲ Intervalo VIP", callback_data="set_vip_interval")
    builder.button(text="▶ Ejecutar Ahora", callback_data="run_schedulers_now")
    builder.button(text="🔙 Volver", callback_data="admin_config")
    builder.adjust(1)
    return builder.as_markup()
