from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from utils.text_utils import sanitize_text

from keyboards.admin_main_kb import get_admin_main_kb
from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip_member
from utils.keyboard_utils import get_main_menu_keyboard
from utils.messages import BOT_MESSAGES
from utils.menu_utils import send_menu, send_clean_message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot):
    user_id = message.from_user.id

    # Ensure the user exists in the database so profile related features work
    user = await session.get(User, user_id)
    if not user:
        user = User(
            id=user_id,
            username=sanitize_text(message.from_user.username),
            first_name=sanitize_text(message.from_user.first_name),
            last_name=sanitize_text(message.from_user.last_name),
        )
        session.add(user)
        await session.commit()

    if is_admin(user_id):
        # Show the admin main menu directly when an administrator runs /start
        await send_menu(
            message,
            "Men\u00fa de administraci\u00f3n",
            get_admin_main_kb(),
            session,
            "admin_main",
        )
    elif await is_vip_member(bot, user_id, session=session):
        await send_clean_message(
            message,
            BOT_MESSAGES["start_welcome_returning_user"],
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await send_clean_message(
            message,
            "Bienvenido al canal free!",
            reply_markup=get_subscription_kb(),
        )
