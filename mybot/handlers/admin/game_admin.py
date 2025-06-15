from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from utils.user_roles import is_admin
from utils.menu_utils import update_menu
from utils.keyboard_utils import (
    get_admin_manage_users_keyboard,
    get_admin_users_list_keyboard,
    get_back_keyboard,
    get_custom_reaction_keyboard,
    get_admin_manage_content_keyboard,
)
from utils.admin_state import AdminUserStates, AdminContentStates
from services.point_service import PointService
from services.config_service import ConfigService
from database.models import User
from utils.config import VIP_CHANNEL_ID

router = Router()


async def show_users_page(message: Message, session: AsyncSession, offset: int) -> None:
    """Display a paginated list of users with action buttons."""
    limit = 5
    if offset < 0:
        offset = 0

    total_stmt = select(func.count()).select_from(User)
    total_result = await session.execute(total_stmt)
    total_users = total_result.scalar_one()

    stmt = (
        select(User)
        .order_by(User.id)
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    users = result.scalars().all()

    text_lines = [
        "👥 Gestión de Usuarios",
        f"Mostrando {offset + 1}-{min(offset + limit, total_users)} de {total_users}",
        "",
    ]

    for user in users:
        display = user.username or (user.first_name or "Sin nombre")
        text_lines.append(f"- {display} (ID: {user.id}) - {user.points} pts")

    keyboard = get_admin_users_list_keyboard(users, offset, total_users, limit)

    await message.edit_text("\n".join(text_lines), reply_markup=keyboard)


@router.callback_query(F.data == "admin_manage_users")
async def admin_manage_users(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await show_users_page(callback.message, session, 0)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_users_page_"))
async def admin_users_page(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    try:
        offset = int(callback.data.split("_")[-1])
    except ValueError:
        offset = 0
    await show_users_page(callback.message, session, offset)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_add_"))
async def admin_user_add(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(points_operation="add", target_user=user_id)
    await callback.message.answer(
        f"Ingresa la cantidad de puntos a sumar a {user_id}:",
        reply_markup=get_back_keyboard("admin_manage_users"),
    )
    await state.set_state(AdminUserStates.assigning_points_amount)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_deduct_"))
async def admin_user_deduct(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(points_operation="deduct", target_user=user_id)
    await callback.message.answer(
        f"Ingresa la cantidad de puntos a restar a {user_id}:",
        reply_markup=get_back_keyboard("admin_manage_users"),
    )
    await state.set_state(AdminUserStates.assigning_points_amount)
    await callback.answer()


@router.message(AdminUserStates.assigning_points_amount)
async def process_points_amount(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Cantidad inválida. Ingresa un número.")
        return
    user_id = data.get("target_user")
    op = data.get("points_operation")
    service = PointService(session)
    if op == "add":
        await service.add_points(user_id, amount)
        await message.answer(f"Se han sumado {amount} puntos a {user_id}.")
    else:
        await service.deduct_points(user_id, amount)
        await message.answer(f"Se han restado {amount} puntos a {user_id}.")
    await state.clear()


@router.callback_query(F.data.startswith("admin_user_view_"))
async def admin_view_user(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    user_id = int(callback.data.split("_")[-1])
    user = await session.get(User, user_id)
    if not user:
        await callback.answer("Usuario no encontrado", show_alert=True)
        return
    display = user.username or (user.first_name or "Sin nombre")
    await callback.message.answer(f"Perfil de {display}\nPuntos: {user.points}")
    await callback.answer()


@router.callback_query(F.data == "admin_search_user")
async def admin_search_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Ingresa un ID o nombre de usuario:",
        reply_markup=get_back_keyboard("admin_manage_users"),
    )
    await state.set_state(AdminUserStates.search_user_query)
    await callback.answer()


@router.message(AdminUserStates.search_user_query)
async def process_search_user(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    query = message.text.strip()
    users = []
    if query.isdigit():
        user = await session.get(User, int(query))
        if user:
            users = [user]
    else:
        stmt = select(User).where(
            (User.username.ilike(f"%{query}%")) |
            (User.first_name.ilike(f"%{query}%")) |
            (User.last_name.ilike(f"%{query}%"))
        ).limit(10)
        result = await session.execute(stmt)
        users = result.scalars().all()

    if not users:
        await message.answer("No se encontraron usuarios.")
    else:
        response = "Resultados:\n" + "\n".join(
            f"- {(u.username or u.first_name or 'Sin nombre')} (ID: {u.id})" for u in users
        )
        await message.answer(response)
    await state.clear()


@router.callback_query(F.data == "admin_send_channel_post")
async def admin_send_channel_post(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.answer(
        "Envía el texto que deseas publicar en el canal:",
        reply_markup=get_back_keyboard("admin_manage_content"),
    )
    await state.set_state(AdminContentStates.waiting_for_channel_post_text)
    await callback.answer()


@router.message(AdminContentStates.waiting_for_channel_post_text)
async def process_channel_post(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    config = ConfigService(session)
    buttons_raw = await config.get_value("reaction_buttons")
    buttons = [b.strip() for b in buttons_raw.split(";") if b.strip()] if buttons_raw else ["👍", "👎"]

    sent = await bot.send_message(
        chat_id=VIP_CHANNEL_ID,
        text=message.text,
        reply_markup=get_custom_reaction_keyboard(0, buttons),
    )

    real_id = sent.message_id
    await bot.edit_message_reply_markup(
        chat_id=VIP_CHANNEL_ID,
        message_id=real_id,
        reply_markup=get_custom_reaction_keyboard(real_id, buttons),
    )

    await message.answer(
        f"Mensaje publicado con ID {real_id}",
        reply_markup=get_admin_manage_content_keyboard(),
    )
    await state.clear()

