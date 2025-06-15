from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from utils.user_roles import is_admin
from utils.menu_utils import update_menu
from keyboards.admin_config_kb import get_admin_config_kb

router = Router()


@router.callback_query(F.data == "admin_config")
async def config_menu(callback: CallbackQuery, session: AsyncSession):
    """Placeholder bot configuration menu."""
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Configuraci\u00f3n del bot",
        get_admin_config_kb(),
        session,
        "admin_config",
    )
    await callback.answer()
