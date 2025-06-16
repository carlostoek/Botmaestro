from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_vip_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Estadísticas", callback_data="vip_stats")
    builder.button(text="🔗 Crear Invitación", callback_data="vip_invite")
    builder.button(text="🔑 Generar Token", callback_data="vip_generate_token")
    builder.button(text="🔗 Generar Enlace", callback_data="vip_generate_link")
    builder.button(text="👥 Suscriptores", callback_data="vip_manage")
    builder.button(text="⚙️ Configuración", callback_data="vip_config")
    builder.button(text="🔙 Volver", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()
