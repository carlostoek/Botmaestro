from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.admin_main_kb import get_admin_main_kb
from keyboards.vip_kb import get_vip_kb
from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip_member

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer(
            "Bienvenido, administrador!",
            reply_markup=get_admin_main_kb(),
        )
    elif await is_vip_member(message.bot, user_id):
        await message.answer(
            "Bienvenido, suscriptor VIP!",
            reply_markup=get_vip_kb(),
        )
    else:
        await message.answer(
            "Bienvenido al canal free!",
            reply_markup=get_subscription_kb(),
        )
