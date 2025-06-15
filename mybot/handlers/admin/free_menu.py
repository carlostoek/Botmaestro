from aiogram import Router, F
from aiogram.types import CallbackQuery
from utils.user_roles import is_admin

router = Router()


@router.callback_query(F.data == "admin_free")
async def free_menu(callback: CallbackQuery):
    """Placeholder Free channel admin menu."""
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text("Secci\u00f3n Free en construcci\u00f3n")
    await callback.answer()
