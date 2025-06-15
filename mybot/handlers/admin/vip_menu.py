from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from utils.user_roles import is_admin, is_vip_member
from keyboards.admin_vip_kb import get_admin_vip_kb
from keyboards.vip_kb import get_vip_kb
from services import TokenService, SubscriptionService, ConfigService
from utils.admin_state import push_state

router = Router()


@router.callback_query(F.data == "admin_vip")
async def vip_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    push_state(callback.from_user.id, "vip")
    await callback.message.edit_text(
        "Administración del VIP", reply_markup=get_admin_vip_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "vip_invite")
async def create_invite(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    token_service = TokenService(session)
    token = await token_service.create_token(callback.from_user.id)
    await callback.message.edit_text(
        f"Invitación generada: {token.token}", reply_markup=get_admin_vip_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "vip_stats")
async def vip_stats(callback: CallbackQuery, session: AsyncSession):
    """Show VIP subscription statistics."""
    if not is_admin(callback.from_user.id):
        return await callback.answer()

    push_state(callback.from_user.id, "vip_stats")
    sub_service = SubscriptionService(session)
    total, active, expired = await sub_service.get_statistics()

    text = (
        f"Suscripciones totales: {total}\n"
        f"Activas: {active}\n"
        f"Expiradas: {expired}"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_vip_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("vip_manage"))
async def manage_subs(callback: CallbackQuery, session: AsyncSession):
    """List active VIP subscribers with simple pagination."""
    if not is_admin(callback.from_user.id):
        return await callback.answer()

    # Extract page from callback data: vip_manage or vip_manage:1
    parts = callback.data.split(":")
    page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

    push_state(callback.from_user.id, "vip_manage")

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
    builder.button(text="🔙 Volver", callback_data="admin_back")
    builder.adjust(2)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "vip_config")
async def vip_config(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = ConfigService(session)
    price = await config.get_value("vip_price")
    price_text = price or "No establecido"
    await callback.message.edit_text(
        f"Precio actual del VIP: {price_text}", reply_markup=get_admin_vip_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "vip_game")
async def vip_game(callback: CallbackQuery):
    if not await is_vip_member(callback.bot, callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Accede al Juego del Diván", reply_markup=get_vip_kb()
    )
    await callback.answer()
