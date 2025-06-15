from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command

from keyboards.vip_kb import get_vip_kb
from utils.user_roles import is_vip_member
from services.subscription_service import SubscriptionService

router = Router()


@router.message(Command("vip_menu"))
async def vip_menu(message: Message, session: AsyncSession):
    if not await is_vip_member(message.bot, message.from_user.id):
        return
    sub_service = SubscriptionService(session)
    sub = await sub_service.get_subscription(message.from_user.id)
    status = "Activa" if sub else "Sin registro"
    await message.answer(
        f"Suscripción VIP: {status}", reply_markup=get_vip_kb()
    )


@router.callback_query(F.data == "vip_subscription")
async def vip_subscription(callback: CallbackQuery, session: AsyncSession):
    if not await is_vip_member(callback.bot, callback.from_user.id):
        return await callback.answer()
    sub_service = SubscriptionService(session)
    sub = await sub_service.get_subscription(callback.from_user.id)
    text = "No registrada" if not sub else f"Válida hasta {sub.expires_at}"
    await callback.message.edit_text(text, reply_markup=get_vip_kb())
    await callback.answer()

