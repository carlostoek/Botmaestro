from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip

router = Router()


@router.message(Command("subscribe"))
async def subscription_menu(message: Message):
    if is_admin(message.from_user.id) or is_vip(message.from_user.id):
        return
    await message.answer(
        "Menú para usuarios del canal free",
        reply_markup=get_subscription_kb(),
    )


@router.callback_query(F.data == "free_button")
async def request_access(callback: CallbackQuery):
    await callback.answer("Acceso solicitado", show_alert=True)
