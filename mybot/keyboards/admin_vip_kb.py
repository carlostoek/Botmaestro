from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_vip_kb():
    """Keyboard for VIP administration menu."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Administración", callback_data="vip_admin_tools")
    builder.button(text="Configuración", callback_data="vip_admin_config")
    builder.button(text="🔙 Volver", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()


def get_vip_admin_tools_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Estadísticas", callback_data="vip_admin_stats")
    builder.button(text="🔗 Generar enlace", callback_data="vip_admin_gen_link")
    builder.button(text="👥 Suscriptores", callback_data="vip_admin_list")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(1)
    return builder.as_markup()


def get_vip_admin_settings_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Definir precio", callback_data="vip_admin_set_price")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(1)
    return builder.as_markup()


def get_price_period_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="1 día", callback_data="vip_price:1d")
    builder.button(text="1 semana", callback_data="vip_price:1w")
    builder.button(text="2 semanas", callback_data="vip_price:2w")
    builder.button(text="1 mes", callback_data="vip_price:1m")
    builder.button(text="Permanente", callback_data="vip_price:perm")
    builder.button(text="🔙 Volver", callback_data="vip_admin_config")
    builder.adjust(1)
    return builder.as_markup()
