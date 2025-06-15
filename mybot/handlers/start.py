from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.admin_kb import get_admin_kb
from keyboards.vip_kb import get_vip_kb
from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Welcome, admin!", reply_markup=get_admin_kb())
    elif is_vip(user_id):
        await message.answer("Welcome, VIP subscriber!", reply_markup=get_vip_kb())
    else:
        await message.answer(
            "Welcome! Please consider subscribing.",
            reply_markup=get_subscription_kb(),
        )
