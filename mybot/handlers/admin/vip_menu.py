from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from utils.user_roles import is_admin, is_vip_member
from keyboards.admin_vip_kb import get_admin_vip_kb
from keyboards.vip_kb import get_vip_kb
from services import TokenService, SubscriptionService, ConfigService

router = Router()


@router.callback_query(F.data == "admin_vip")
async def vip_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
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


@router.callback_query(F.data == "vip_manage")
async def manage_subs(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    result = await session.execute("SELECT COUNT(*) FROM vip_subscriptions")
    count = result.scalar() or 0
    await callback.message.edit_text(
        f"Suscriptores activos: {count}", reply_markup=get_admin_vip_kb()
    )
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
