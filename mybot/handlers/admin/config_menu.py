from aiogram import Router, F
from aiogram.types import CallbackQuery
from utils.user_roles import is_admin

router = Router()


@router.callback_query(F.data == "admin_config")
async def config_menu(callback: CallbackQuery):
    """Placeholder bot configuration menu."""
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text("Configuraci\u00f3n del bot en construcci\u00f3n")
    await callback.answer()
