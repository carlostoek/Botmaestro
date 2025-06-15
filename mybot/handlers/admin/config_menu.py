from aiogram import Router, F
from aiogram.types import CallbackQuery
from utils.user_roles import is_admin
from keyboards.admin_config_kb import get_config_menu_kb

router = Router()


@router.callback_query(F.data == "admin_config")
async def config_menu(callback: CallbackQuery):
    """Show bot configuration menu."""
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text("Configuraci\u00f3n", reply_markup=get_config_menu_kb())
    await callback.answer()
