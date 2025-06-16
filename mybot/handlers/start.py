from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User

from keyboards.admin_main_kb import get_admin_main_kb
from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip_member
from utils.keyboard_utils import get_main_menu_keyboard
from utils.messages import BOT_MESSAGES

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot):
    user_id = message.from_user.id

    # Ensure the user exists in the database so profile related features work
    user = await session.get(User, user_id)
    if not user:
        user = User(
            id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        session.add(user)
        await session.commit()

    if is_admin(user_id):
        await message.answer(
            "Bienvenido, administrador!",
            reply_markup=get_admin_main_kb(),
        )
    elif await is_vip_member(bot, user_id):
        await message.answer(
            BOT_MESSAGES["start_welcome_returning_user"],
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await message.answer(
            "Bienvenido al canal free!",
            reply_markup=get_subscription_kb(),
        )
