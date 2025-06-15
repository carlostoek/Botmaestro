from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_vip_config_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 Tarifas", callback_data="config_tarifas")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(1)
    return builder.as_markup()


def get_tariff_select_kb(tariffs):
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:
        builder.button(text=tariff.name, callback_data=f"generate_token_{tariff.id}")
    builder.adjust(1)
    return builder.as_markup()
