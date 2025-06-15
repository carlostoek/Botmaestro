from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.vip_kb import get_vip_kb
from utils.user_roles import is_vip

router = Router()


@router.message(Command("vip_menu"))
async def vip_menu(message: Message):
    if not is_vip(message.from_user.id):
        return
    await message.answer("Menú para suscriptores VIP", reply_markup=get_vip_kb())


@router.callback_query(F.data == "vip_button")
async def vip_placeholder_handler(callback: CallbackQuery):
    await callback.answer("Acción de suscriptor VIP")
