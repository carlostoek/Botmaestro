from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.admin_kb import get_admin_kb
from utils.user_roles import is_admin

router = Router()


@router.message(Command("admin_menu"))
async def admin_menu(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Admin menu", reply_markup=get_admin_kb())


@router.callback_query(F.data == "admin_placeholder")
async def admin_placeholder_handler(callback: CallbackQuery):
    await callback.answer("Admin action placeholder")
