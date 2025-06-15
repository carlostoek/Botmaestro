from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from utils.user_roles import is_admin, is_vip_member
from keyboards.admin_vip_kb import (
    get_admin_vip_kb,
    get_vip_admin_tools_kb,
    get_vip_admin_settings_kb,
)
from keyboards.vip_kb import get_vip_kb
from services import SubscriptionService, TokenService, ConfigService

router = Router()

# Temporary store when an admin is entering a price
_waiting_price: dict[int, str] = {}


@router.callback_query(F.data == "admin_vip")
async def vip_menu(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    if is_admin(user_id):
        await callback.message.edit_text("Adm. Diván", reply_markup=get_admin_vip_kb())
        await callback.answer()
        return

    if await is_vip_member(callback.bot, user_id):
        service = SubscriptionService(session)
        sub = await service.get_subscription(user_id)
        text = (
            f"Suscripción activa hasta {sub.end_date.date()}"
            if sub
            else "No tienes una suscripción activa."
        )
        await callback.message.edit_text(text, reply_markup=get_vip_kb())
        await callback.answer()
        return

    await callback.answer()


@router.callback_query(F.data == "vip_admin_tools")
async def vip_admin_tools(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text("Administración", reply_markup=get_vip_admin_tools_kb())
    await callback.answer()


@router.callback_query(F.data == "vip_admin_config")
async def vip_admin_config(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text("Configuración", reply_markup=get_vip_admin_settings_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("vip_price:"))
async def vip_set_price_period(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    period = callback.data.split(":", 1)[1]
    _waiting_price[callback.from_user.id] = period
    await callback.message.edit_text("Ingresa el precio para este período")
    await callback.answer()


@router.message(lambda m: m.from_user and m.from_user.id in _waiting_price)
async def vip_price_input(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    period = _waiting_price.pop(user_id, None)
    if period is None:
        return
    if not message.text.isdigit():
        await message.answer("Ingresa solo números")
        return
    service = ConfigService(session)
    await service.set_price(period, message.text.strip())
    await message.answer("Precio actualizado")


@router.callback_query(F.data == "vip_admin_gen_link")
async def vip_admin_gen_link(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    tokens = TokenService(session)
    token = await tokens.generate_token(7)
    bot_username = (await callback.bot.me()).username
    link = f"https://t.me/{bot_username}?start={token}"
    await callback.message.edit_text(f"Enlace generado: {link}", reply_markup=get_vip_admin_tools_kb())
    await callback.answer()


@router.callback_query(F.data == "vip_admin_list")
async def vip_admin_list(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    service = SubscriptionService(session)
    subs = await service.list_active_subscriptions()
    if not subs:
        await callback.message.edit_text("No hay suscriptores activos", reply_markup=get_vip_admin_tools_kb())
        await callback.answer()
        return
    text = "\n".join([f"{sub.user_id} → {sub.end_date.date()}" for sub in subs])
    await callback.message.edit_text(text, reply_markup=get_vip_admin_tools_kb())
    await callback.answer()
