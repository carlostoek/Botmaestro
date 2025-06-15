from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.vip_kb import get_vip_kb
from .game_menu import router as game_router
from utils.user_roles import is_vip_member
from services.subscription_service import SubscriptionService

router = Router()
router.include_router(game_router)


@router.message(Command("vip_menu"))
async def vip_menu(message: Message, session: AsyncSession):
    if not await is_vip_member(message.bot, message.from_user.id):
        return
    await message.answer("Menú para suscriptores VIP", reply_markup=get_vip_kb())


@router.callback_query(F.data == "vip_subscription")
async def vip_subscription(callback: CallbackQuery, session: AsyncSession):
    if not await is_vip_member(callback.bot, callback.from_user.id):
        return await callback.answer()

    service = SubscriptionService(session)
    sub = await service.get_subscription(callback.from_user.id)
    if sub:
        text = f"Suscripción activa hasta {sub.end_date.date()}"
    else:
        text = "No tienes una suscripción activa."
    await callback.message.edit_text(text, reply_markup=get_vip_kb())
    await callback.answer()
