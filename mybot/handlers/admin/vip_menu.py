from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from utils.user_roles import is_admin, is_vip_member
from keyboards.admin_vip_kb import get_admin_vip_kb
from keyboards.admin_vip_config_kb import (
    get_admin_vip_config_kb,
    get_tariff_select_kb,
    get_vip_messages_kb,
)
from keyboards.vip_kb import get_vip_kb
from utils.keyboard_utils import get_back_keyboard
from services import (
    SubscriptionService,
    ConfigService,
    TokenService,
    get_admin_statistics,
)
from database.models import User
from utils.text_utils import sanitize_text
from utils.admin_state import AdminVipMessageStates
from aiogram.fsm.context import FSMContext
from database.models import Tariff
from utils.menu_utils import update_menu
from database.models import set_user_menu_state

router = Router()


@router.callback_query(F.data == "admin_vip")
async def vip_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "El Diván",
        get_admin_vip_kb(),
        session,
        "admin_vip",
    )
    await callback.answer()



@router.callback_query(F.data == "vip_generate_token")
async def vip_generate_token(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    result = await session.execute(select(Tariff))
    tariffs = result.scalars().all()
    builder = InlineKeyboardBuilder()
    for t in tariffs:
        builder.button(text=t.name, callback_data=f"vip_token_{t.id}")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(1)
    await update_menu(
        callback,
        "Elige la tarifa para generar token:",
        builder.as_markup(),
        session,
        "admin_vip",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("vip_token_"))
async def vip_create_token(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    tariff_id = int(callback.data.split("_")[-1])
    service = TokenService(session)
    token = await service.create_vip_token(tariff_id)
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={token.token_string}"
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Invalidar", callback_data=f"vip_invalidate_{token.token_string}")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(1)
    await callback.message.edit_text(
        f"Enlace generado: {link}", reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("vip_invalidate_"))
async def vip_invalidate_token(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    token_string = callback.data.split("_")[-1]
    service = TokenService(session)
    await service.invalidate_vip_token(token_string)
    await callback.answer("Token invalidado", show_alert=True)



@router.callback_query(F.data == "vip_stats")
async def vip_stats(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    stats = await get_admin_statistics(session)
    text_lines = [
        "*Estad\xc3\xadsticas del sistema*",
        f"\n*Usuarios totales:* {stats['users_total']}",
        f"*Suscripciones totales:* {stats['subscriptions_total']}",
        f"*Activas:* {stats['subscriptions_active']}",
        f"*Expiradas:* {stats['subscriptions_expired']}",
    ]
    revenue = stats.get("revenue_total")
    if revenue:
        text_lines.append(f"*Recaudaci\xc3\xb3n:* {revenue}")
    else:
        text_lines.append("*Recaudaci\xc3\xb3n:* No disponible")

    builder = InlineKeyboardBuilder()
    builder.button(text="\ud83d\udd19 Volver al men\xc3\xba", callback_data="admin_vip")
    builder.adjust(1)
    await callback.message.edit_text(
        "\n".join(text_lines), reply_markup=builder.as_markup(), parse_mode="Markdown"
    )
    await set_user_menu_state(session, callback.from_user.id, "admin_vip")
    await callback.answer()


@router.callback_query(F.data.startswith("vip_manage"))
async def manage_subs(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    parts = callback.data.split(":")
    page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    sub_service = SubscriptionService(session)
    subs = await sub_service.get_active_subscribers()
    page_size = 10
    start = page * page_size
    current = subs[start : start + page_size]

    lines = []
    builder = InlineKeyboardBuilder()
    for i, sub in enumerate(current):
        user = await session.get(User, sub.user_id)
        username = sanitize_text(user.username) if user else None
        display = "No disponible"
        if username:
            display = username.splitlines()[0]
        lines.append(f"{i+start+1}. {display} (ID: {sub.user_id})")
        builder.button(text="➕", callback_data=f"vip_extend_{sub.user_id}")
        builder.button(text="❌", callback_data=f"vip_revoke_{sub.user_id}")
        builder.row()

    text = (
        "Suscriptores VIP activos:\n" + "\n".join(lines)
        if lines
        else "No hay suscriptores activos."
    )

    if start > 0:
        builder.button(text="⬅️", callback_data=f"vip_manage:{page - 1}")
    if start + page_size < len(subs):
        builder.button(text="➡️", callback_data=f"vip_manage:{page + 1}")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(2)

    await update_menu(callback, text, builder.as_markup(), session, "admin_vip")
    await callback.answer()


@router.callback_query(F.data.startswith("vip_extend_"))
async def vip_extend(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    user_id = int(callback.data.split("_")[-1])
    sub_service = SubscriptionService(session)
    await sub_service.extend_subscription(user_id, 30)
    await callback.answer("Suscripción extendida", show_alert=True)


@router.callback_query(F.data.startswith("vip_revoke_"))
async def vip_revoke(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    user_id = int(callback.data.split("_")[-1])
    sub_service = SubscriptionService(session)
    await sub_service.revoke_subscription(user_id)
    await callback.answer("Suscripción revocada", show_alert=True)


@router.callback_query(F.data == "vip_config")
async def vip_config(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = ConfigService(session)
    price = await config.get_value("vip_price")
    price_text = price or "No establecido"
    await update_menu(
        callback,
        f"Precio actual del VIP: {price_text}",
        get_admin_vip_config_kb(),
        session,
        "vip_config",
    )
    await callback.answer()


@router.callback_query(F.data == "vip_config_messages")
async def vip_config_messages(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Configura los mensajes del canal VIP",
        get_vip_messages_kb(),
        session,
        "vip_message_config",
    )
    await callback.answer()


@router.callback_query(F.data == "edit_vip_reminder")
async def prompt_vip_reminder(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = ConfigService(session)
    current = await config.get_value("vip_reminder_message") or "Tu suscripción VIP expira pronto."
    await callback.message.edit_text(
        f"Mensaje de recordatorio actual:\n{current}\n\nEnvía el nuevo mensaje:",
        reply_markup=get_back_keyboard("vip_config_messages"),
    )
    await state.set_state(AdminVipMessageStates.waiting_for_reminder_message)
    await callback.answer()


@router.callback_query(F.data == "edit_vip_farewell")
async def prompt_vip_farewell(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = ConfigService(session)
    current = await config.get_value("vip_farewell_message") or "Tu suscripción VIP ha expirado."
    await callback.message.edit_text(
        f"Mensaje de despedida actual:\n{current}\n\nEnvía el nuevo mensaje:",
        reply_markup=get_back_keyboard("vip_config_messages"),
    )
    await state.set_state(AdminVipMessageStates.waiting_for_farewell_message)
    await callback.answer()


@router.message(AdminVipMessageStates.waiting_for_reminder_message, F.text)
async def set_vip_reminder(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    config = ConfigService(session)
    await config.set_value("vip_reminder_message", message.text)
    await message.answer("Mensaje de recordatorio actualizado.", reply_markup=get_vip_messages_kb())
    await state.clear()


@router.message(AdminVipMessageStates.waiting_for_farewell_message, F.text)
async def set_vip_farewell(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    config = ConfigService(session)
    await config.set_value("vip_farewell_message", message.text)
    await message.answer("Mensaje de despedida actualizado.", reply_markup=get_vip_messages_kb())
    await state.clear()


@router.callback_query(F.data == "vip_game")
async def vip_game(callback: CallbackQuery, session: AsyncSession):
    if not await is_vip_member(callback.bot, callback.from_user.id, session=session):
        return await callback.answer()
    await callback.message.edit_text(
        "Accede al Juego del Diván", reply_markup=get_vip_kb()
    )
    await callback.answer()
