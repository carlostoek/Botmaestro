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
)
from utils.admin_state import AdminVipMessageStates
from aiogram.fsm.context import FSMContext
from database.models import Tariff
from utils.menu_utils import update_menu

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
    await update_menu(
        callback,
        "Elige la tarifa para generar token:",
        get_tariff_select_kb(tariffs),
        session,
        "admin_vip",
    )
    await callback.answer()



@router.callback_query(F.data == "vip_stats")
async def vip_stats(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    sub_service = SubscriptionService(session)
    total, active, expired = await sub_service.get_statistics()
    text = f"Suscripciones totales: {total}\nActivas: {active}\nExpiradas: {expired}"
    await update_menu(callback, text, get_admin_vip_kb(), session, "admin_vip")
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

    lines = [f"{i+start+1}. {sub.user_id}" for i, sub in enumerate(current)]
    text = (
        "Suscriptores VIP activos:\n" + "\n".join(lines)
        if lines
        else "No hay suscriptores activos."
    )

    builder = InlineKeyboardBuilder()
    if start > 0:
        builder.button(text="⬅️", callback_data=f"vip_manage:{page - 1}")
    if start + page_size < len(subs):
        builder.button(text="➡️", callback_data=f"vip_manage:{page + 1}")
    builder.button(text="🔙 Volver", callback_data="admin_vip")
    builder.adjust(2)

    await update_menu(callback, text, builder.as_markup(), session, "admin_vip")
    await callback.answer()


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
    config = ConfigService(session)
    reminder = await config.get_value("vip_reminder_message") or "Tu suscripción VIP expira pronto."
    farewell = await config.get_value("vip_farewell_message") or "Tu suscripción VIP ha expirado."
    text = (
        "Mensajes VIP actuales:\n"
        f"Recordatorio: {reminder}\n\n"
        f"Despedida: {farewell}"
    )
    await update_menu(
        callback,
        text,
        get_vip_messages_kb(),
        session,
        "vip_message_config",
    )
    await callback.answer()


@router.callback_query(F.data == "edit_vip_reminder")
async def prompt_vip_reminder(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Envía el nuevo mensaje de recordatorio:",
        reply_markup=get_back_keyboard("vip_config_messages"),
    )
    await state.set_state(AdminVipMessageStates.waiting_for_reminder_message)
    await callback.answer()


@router.callback_query(F.data == "edit_vip_farewell")
async def prompt_vip_farewell(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Envía el nuevo mensaje de despedida:",
        reply_markup=get_back_keyboard("vip_config_messages"),
    )
    await state.set_state(AdminVipMessageStates.waiting_for_farewell_message)
    await callback.answer()


@router.message(AdminVipMessageStates.waiting_for_reminder_message)
async def set_vip_reminder(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    config = ConfigService(session)
    await config.set_value("vip_reminder_message", message.text)
    await message.answer("Mensaje de recordatorio actualizado.", reply_markup=get_vip_messages_kb())
    await state.clear()


@router.message(AdminVipMessageStates.waiting_for_farewell_message)
async def set_vip_farewell(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    config = ConfigService(session)
    await config.set_value("vip_farewell_message", message.text)
    await message.answer("Mensaje de despedida actualizado.", reply_markup=get_vip_messages_kb())
    await state.clear()


@router.callback_query(F.data == "vip_game")
async def vip_game(callback: CallbackQuery):
    if not await is_vip_member(callback.bot, callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Accede al Juego del Diván", reply_markup=get_vip_kb()
    )
    await callback.answer()
