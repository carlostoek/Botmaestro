from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
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
    get_admin_content_missions_keyboard,
    get_admin_content_badges_keyboard,
    get_admin_content_levels_keyboard,
    get_admin_content_rewards_keyboard,
    get_admin_content_auctions_keyboard,
    get_admin_content_daily_gifts_keyboard,
    get_admin_content_minigames_keyboard,
)
from utils.admin_state import (
    AdminUserStates,
    AdminContentStates,
    AdminMissionStates,
    AdminDailyGiftStates,
    AdminRewardStates,
)
from services.mission_service import MissionService
from services.reward_service import RewardService
from database.models import User, Mission
from services.point_service import PointService
from services.config_service import ConfigService
from utils.config import VIP_CHANNEL_ID
from utils.messages import BOT_MESSAGES

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


@router.callback_query(F.data == "admin_content_missions")
async def admin_content_missions(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "📌 Misiones - Selecciona una opción:",
        get_admin_content_missions_keyboard(),
        session,
        "admin_content_missions",
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_daily_gift")
async def toggle_daily_gift(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    service = ConfigService(session)
    current = await service.get_value("daily_gift_enabled")
    new_value = "false" if current == "true" else "true"
    await service.set_value("daily_gift_enabled", new_value)
    await callback.answer("Configuración actualizada", show_alert=True)
    await admin_content_daily_gifts(callback, session)


@router.callback_query(F.data == "admin_create_mission")
async def admin_start_create_mission(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Ingresa el nombre de la misión:",
        reply_markup=get_back_keyboard("admin_content_missions"),
    )
    await state.set_state(AdminMissionStates.creating_mission_name)
    await callback.answer()


@router.message(AdminMissionStates.creating_mission_name)
async def admin_process_mission_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text)
    await message.answer("Ingresa la descripción de la misión:")
    await state.set_state(AdminMissionStates.creating_mission_description)


@router.message(AdminMissionStates.creating_mission_description)
async def admin_process_mission_description(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(description=message.text)
    await message.answer("¿Cuántos puntos otorgará la misión?")
    await state.set_state(AdminMissionStates.creating_mission_points)


@router.message(AdminMissionStates.creating_mission_points)
async def admin_process_mission_points(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        points = int(message.text)
    except ValueError:
        await message.answer("Ingresa un número válido de puntos:")
        return
    await state.update_data(points_reward=points)
    await message.answer(
        "Tipo de misión (`daily`, `weekly`, `one_time`, `reaction`):"
    )
    await state.set_state(AdminMissionStates.creating_mission_type)


@router.message(AdminMissionStates.creating_mission_type)
async def admin_process_mission_type(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    mission_type = message.text.lower().strip()
    if mission_type not in {"daily", "weekly", "one_time", "reaction"}:
        await message.answer("Tipo inválido. Usa daily, weekly, one_time o reaction:")
        return
    await state.update_data(type=mission_type)
    await message.answer("¿Requiere acción externa para completarse? (si/no):")
    await state.set_state(AdminMissionStates.creating_mission_requires_action)


@router.message(AdminMissionStates.creating_mission_requires_action)
async def admin_process_requires_action(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    text = message.text.lower().strip()
    requires_action = text in {"si", "sí", "s"}
    await state.update_data(requires_action=requires_action)
    await message.answer(
        "Ingresa datos adicionales para la misión en formato JSON o escribe 'no' para omitir:"
    )
    await state.set_state(AdminMissionStates.creating_mission_action_data)


@router.message(AdminMissionStates.creating_mission_action_data)
async def admin_process_action_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    if not is_admin(message.from_user.id):
        return
    action_data_text = message.text.strip()
    action_data = None
    if action_data_text.lower() not in {"no", "none", "-"}:
        try:
            import json

            action_data = json.loads(action_data_text)
        except Exception:
            action_data = {"data": action_data_text}
    await state.update_data(action_data=action_data)
    data = await state.get_data()
    mission_service = MissionService(session)
    await mission_service.create_mission(
        data["name"],
        data["description"],
        data["points_reward"],
        data["type"],
        data.get("requires_action", False),
        data.get("action_data"),
    )
    await message.answer(
        "✅ Misión creada.", reply_markup=get_admin_content_missions_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "admin_toggle_mission")
async def admin_toggle_mission_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    result = await session.execute(select(Mission))
    missions = result.scalars().all()
    keyboard = []
    for m in missions:
        status = "✅" if m.is_active else "❌"
        keyboard.append(
            [InlineKeyboardButton(text=f"{status} {m.name}", callback_data=f"toggle_mission_{m.id}")]
        )
    keyboard.append([InlineKeyboardButton(text="🔙 Volver", callback_data="admin_content_missions")])
    await callback.message.edit_text(
        "Activar o desactivar misiones:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_mission_"))
async def toggle_mission_status(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    mission_id = callback.data.split("toggle_mission_")[-1]
    mission_service = MissionService(session)
    mission = await mission_service.get_mission_by_id(mission_id)
    if not mission:
        await callback.answer("Misión no encontrada", show_alert=True)
        return
    await mission_service.toggle_mission_status(mission_id, not mission.is_active)
    status = "activada" if not mission.is_active else "desactivada"
    await callback.answer(f"Misión {status}", show_alert=True)
    # Refresh list
    result = await session.execute(select(Mission))
    missions = result.scalars().all()
    keyboard = []
    for m in missions:
        status_icon = "✅" if m.is_active else "❌"
        keyboard.append(
            [InlineKeyboardButton(text=f"{status_icon} {m.name}", callback_data=f"toggle_mission_{m.id}")]
        )
    keyboard.append([InlineKeyboardButton(text="🔙 Volver", callback_data="admin_content_missions")])
    await callback.message.edit_text(
        "Activar o desactivar misiones:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data == "admin_view_active_missions")
async def admin_view_active_missions(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    stmt = select(Mission).where(Mission.is_active == True)
    result = await session.execute(stmt)
    missions = result.scalars().all()
    if missions:
        lines = [f"- {m.name} ({m.type}) -> {m.points_reward} pts" for m in missions]
        text = "Misiones activas:\n" + "\n".join(lines)
    else:
        text = "No hay misiones activas."
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("admin_content_missions"),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_content_badges")
async def admin_content_badges(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "🏅 Insignias - Selecciona una opción:",
        get_admin_content_badges_keyboard(),
        session,
        "admin_content_badges",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_content_levels")
async def admin_content_levels(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "📈 Niveles - Selecciona una opción:",
        get_admin_content_levels_keyboard(),
        session,
        "admin_content_levels",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_content_rewards")
async def admin_content_rewards(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "🎁 Recompensas (Catálogo VIP) - Selecciona una opción:",
        get_admin_content_rewards_keyboard(),
        session,
        "admin_content_rewards",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_content_auctions")
async def admin_content_auctions(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "📦 Subastas - Selecciona una opción:",
        get_admin_content_auctions_keyboard(),
        session,
        "admin_content_auctions",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_content_daily_gifts")
async def admin_content_daily_gifts(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = ConfigService(session)
    enabled = (await config.get_value("daily_gift_enabled")) != "false"
    toggle_text = "❌ Desactivar" if enabled else "✅ Activar"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_text, callback_data="toggle_daily_gift")],
            [InlineKeyboardButton(text="🎯 Configurar Regalo del Día", callback_data="admin_configure_daily_gift")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_manage_content")],
        ]
    )
    await update_menu(
        callback,
        "🎁 Regalos Diarios - Selecciona una opción:",
        keyboard,
        session,
        "admin_content_daily_gifts",
    )


@router.callback_query(F.data == "admin_content_minigames")
async def admin_content_minigames(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = ConfigService(session)
    enabled = (await config.get_value("minigames_enabled")) != "false"
    toggle_text = "❌ Desactivar" if enabled else "✅ Activar"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_text, callback_data="toggle_minigames")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_manage_content")],
        ]
    )
    await update_menu(
        callback,
        "🕹 Minijuegos - Configuración:",
        keyboard,
        session,
        "admin_content_minigames",
    )


@router.callback_query(F.data == "toggle_minigames")
async def toggle_minigames(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    service = ConfigService(session)
    current = await service.get_value("minigames_enabled")
    new_value = "false" if current == "true" else "true"
    await service.set_value("minigames_enabled", new_value)
    await callback.answer("Configuración actualizada", show_alert=True)
    await admin_content_minigames(callback, session)


@router.callback_query(F.data == "admin_configure_daily_gift")
async def configure_daily_gift(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Ingresa la cantidad de puntos para el regalo diario:",
        reply_markup=get_back_keyboard("admin_content_daily_gifts"),
    )
    await state.set_state(AdminDailyGiftStates.waiting_for_amount)
    await callback.answer()


@router.message(AdminDailyGiftStates.waiting_for_amount)
async def save_daily_gift_amount(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Ingresa un número válido.")
        return
    service = ConfigService(session)
    await service.set_value("daily_gift_points", str(amount))
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_content_daily_gifts")]
        ]
    )
    await message.answer(
        "Regalo diario actualizado.", reply_markup=keyboard
    )
    await state.clear()


# --- Gestión de Recompensas ---

@router.callback_query(F.data == "admin_create_reward")
async def admin_create_reward(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        BOT_MESSAGES["enter_reward_name"],
        reply_markup=get_back_keyboard("admin_content_rewards"),
    )
    await state.set_state(AdminRewardStates.creating_reward_name)
    await callback.answer()


@router.message(AdminRewardStates.creating_reward_name)
async def process_reward_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text)
    await message.answer(BOT_MESSAGES["enter_reward_description"])
    await state.set_state(AdminRewardStates.creating_reward_description)


@router.message(AdminRewardStates.creating_reward_description)
async def process_reward_description(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(description=message.text)
    await message.answer(BOT_MESSAGES["enter_reward_cost"])
    await state.set_state(AdminRewardStates.creating_reward_cost)


@router.message(AdminRewardStates.creating_reward_cost)
async def process_reward_cost(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        cost = int(message.text)
    except ValueError:
        await message.answer(BOT_MESSAGES["invalid_number"])
        return
    await state.update_data(cost=cost)
    await message.answer(BOT_MESSAGES["enter_reward_stock"])
    await state.set_state(AdminRewardStates.creating_reward_stock)


@router.message(AdminRewardStates.creating_reward_stock)
async def process_reward_stock(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    try:
        stock = int(message.text)
    except ValueError:
        await message.answer(BOT_MESSAGES["invalid_number"])
        return
    data = await state.get_data()
    service = RewardService(session)
    await service.create_reward(data["name"], data["description"], data["cost"], stock)
    await message.answer(
        BOT_MESSAGES["reward_created"], reply_markup=get_admin_content_rewards_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "admin_edit_reward")
async def admin_edit_reward(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    rewards = await RewardService(session).list_rewards()
    keyboard = []
    for r in rewards:
        status = "✅" if r.is_active else "❌"
        keyboard.append([
            InlineKeyboardButton(text=f"{status} {r.name}", callback_data=f"toggle_reward_{r.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Volver", callback_data="admin_content_rewards")])
    await callback.message.edit_text(
        "Activar o desactivar recompensas:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_reward_"))
async def toggle_reward(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    reward_id = int(callback.data.split("toggle_reward_")[-1])
    service = RewardService(session)
    reward = await service.get_reward_by_id(reward_id)
    if not reward:
        await callback.answer("Recompensa no encontrada", show_alert=True)
        return
    await service.toggle_reward_status(reward_id, not reward.is_active)
    # Refresh list
    rewards = await service.list_rewards()
    keyboard = []
    for r in rewards:
        status = "✅" if r.is_active else "❌"
        keyboard.append([
            InlineKeyboardButton(text=f"{status} {r.name}", callback_data=f"toggle_reward_{r.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Volver", callback_data="admin_content_rewards")])
    await callback.message.edit_text(
        "Activar o desactivar recompensas:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await callback.answer()

