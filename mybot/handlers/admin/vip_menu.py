from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from utils.user_roles import is_admin, is_vip_member
from keyboards.admin_vip_kb import get_admin_vip_kb
from keyboards.admin_vip_config_kb import get_admin_vip_config_kb
from keyboards.vip_kb import get_vip_kb
from services import (
    TokenService,
    SubscriptionService,
    ConfigService,
    SubscriptionPlanService,
)
from keyboards.tarifas_kb import get_plan_list_kb
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


@router.callback_query(F.data == "vip_invite")
async def create_invite(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    token_service = TokenService(session)
    token = await token_service.create_token(callback.from_user.id)
    await update_menu(
        callback,
        f"Invitación generada: {token.token}",
        get_admin_vip_kb(),
        session,
        "admin_vip",
    )
    await callback.answer()


@router.callback_query(F.data == "vip_generate_link")
async def generate_link_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    plan_service = SubscriptionPlanService(session)
    plans = await plan_service.list_plans()
    await update_menu(
        callback,
        "Elige un plan para generar enlace",
        get_plan_list_kb(plans),
        session,
        "vip_generate_link",
    )
    await callback.answer()


@router.callback_query(F.data == "vip_generate_link_back")
async def back_from_generate_link(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await vip_menu(callback, session)


@router.callback_query(F.data.startswith("plan_link_"))
async def generate_link(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    plan_id = int(callback.data.split("_")[-1])
    token_service = TokenService(session)
    token = await token_service.create_subscription_token(plan_id, callback.from_user.id)
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={token.token}"
    await update_menu(
        callback,
        f"Enlace generado: {link}",
        get_admin_vip_kb(),
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


@router.callback_query(F.data == "vip_game")
async def vip_game(callback: CallbackQuery):
    if not await is_vip_member(callback.bot, callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Accede al Juego del Diván", reply_markup=get_vip_kb()
    )
    await callback.answer()
