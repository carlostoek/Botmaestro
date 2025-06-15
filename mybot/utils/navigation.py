from aiogram.types import Message
from keyboards.admin_main_kb import get_admin_main_kb
from keyboards.vip_kb import get_vip_kb
from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip_member

async def return_to_parent_menu(message: Message, bot, user_id: int) -> None:
    """Return to the parent menu based on the user's role."""
    if is_admin(user_id):
        await message.edit_text(
            "Menú de administración",
            reply_markup=get_admin_main_kb(),
        )
    elif await is_vip_member(bot, user_id):
        await message.edit_text(
            "Menú para suscriptores VIP",
            reply_markup=get_vip_kb(),
        )
    else:
        await message.edit_text(
            "Para acceder al canal VIP necesitas una suscripción.",
            reply_markup=get_subscription_kb(),
        )
