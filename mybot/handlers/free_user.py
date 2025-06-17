from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip

router = Router()


@router.message(Command("subscribe"))
async def subscription_menu(message: Message):
    if is_admin(message.from_user.id) or await is_vip(message.bot, message.from_user.id):
        return
    await message.answer(
        "Menú para usuarios del canal free",
        reply_markup=get_subscription_kb(),
    )


@router.callback_query(F.data == "free_info")
async def show_info(callback: CallbackQuery):
    """Provide basic information to free users."""
    await callback.answer()
    await callback.message.edit_text(
        "Información sobre el canal y sus beneficios.",
        reply_markup=get_subscription_kb(),
    )


@router.callback_query(F.data == "free_game")
async def free_game(callback: CallbackQuery):
    """Simple placeholder for the free version of the game."""
    await callback.message.edit_text(
        "Versión gratuita del Juego del Diván. ¡Disfruta!",
        reply_markup=get_subscription_kb(),
    )
    await callback.answer()
