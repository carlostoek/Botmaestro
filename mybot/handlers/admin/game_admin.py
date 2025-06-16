from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import datetime

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
)
from services.mission_service import MissionService
from database.models import User, Mission
from services.point_service import PointService
from services.config_service import ConfigService

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

    vip_id = await config.get_vip_channel_id()
    if not vip_id:
        await message.answer("Canal VIP no configurado.", reply_markup=get_admin_manage_content_keyboard())
        await state.clear()
        return
    sent = await bot.send_message(
        chat_id=vip_id,
        text=message.text,
        reply_markup=get_custom_reaction_keyboard(0, buttons),
    )

    real_id = sent.message_id
    await bot.edit_message_reply_markup(
        chat_id=vip_id,
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
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Reaccionar a publicaciones", callback_data="mission_type_reaction")],
            [InlineKeyboardButton(text="📝 Enviar mensajes", callback_data="mission_type_messages")],
            [InlineKeyboardButton(text="📅 Conectarse X días seguidos", callback_data="mission_type_login")],
            [InlineKeyboardButton(text="🎯 Personalizada", callback_data="mission_type_custom")],
        ]
    )
    await message.answer("🎯 Tipo de misión", reply_markup=kb)
    await state.set_state(AdminMissionStates.creating_mission_type)


@router.callback_query(F.data.startswith("mission_type_"))
async def admin_select_mission_type(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    m_type = callback.data.split("mission_type_")[-1]
    mapping = {
        "reaction": "reaction",
        "messages": "messages",
        "login": "login_streak",
        "custom": "custom",
    }
    await state.update_data(type=mapping.get(m_type, m_type))
    await callback.message.edit_text("📊 Cantidad requerida")
    await state.set_state(AdminMissionStates.creating_mission_target)
    await callback.answer()


@router.message(AdminMissionStates.creating_mission_target)
async def admin_process_target(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        value = int(message.text)
    except ValueError:
        await message.answer("Ingresa un número válido:")
        return
    await state.update_data(target=value)
    await message.answer("🏆 Recompensa en puntos")
    await state.set_state(AdminMissionStates.creating_mission_reward)


@router.message(AdminMissionStates.creating_mission_reward)
async def admin_process_reward(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        points = int(message.text)
    except ValueError:
        await message.answer("Ingresa un número válido de puntos:")
        return
    await state.update_data(reward=points)
    await message.answer("⏳ Duración (en días, 0 para permanente)")
    await state.set_state(AdminMissionStates.creating_mission_duration)


@router.message(AdminMissionStates.creating_mission_duration)
async def admin_process_duration(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    try:
        days = int(message.text)
    except ValueError:
        await message.answer("Ingresa un número válido de días:")
        return
    data = await state.get_data()
    mission_service = MissionService(session)
    await mission_service.create_mission(
        data["name"],
        data["description"],
        data["type"],
        data["target"],
        data["reward"],
        days,
    )
    await message.answer(
        "✅ Misión creada correctamente", reply_markup=get_admin_content_missions_keyboard()
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


@router.callback_query(F.data == "admin_view_missions")
async def admin_view_active_missions(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    stmt = select(Mission).where(Mission.is_active == True)
    result = await session.execute(stmt)
    missions = result.scalars().all()
    now = datetime.datetime.utcnow()
    lines = []
    for m in missions:
        remaining = "∞"
        if m.duration_days:
            end = m.created_at + datetime.timedelta(days=m.duration_days)
            remaining = str((end - now).days)
        lines.append(f"🗒️ {m.name} | 📊 {m.target_value} | 🎁 {m.points_reward} | ⏳ {remaining}d")
    text = "Misiones activas:" if lines else "No hay misiones activas."
    if lines:
        text += "\n" + "\n".join(lines)
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("admin_content_missions"),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_delete_mission")
async def admin_delete_mission_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    result = await session.execute(select(Mission))
    missions = result.scalars().all()
    keyboard = [[InlineKeyboardButton(text=m.name, callback_data=f"delete_mission_{m.id}")] for m in missions]
    keyboard.append([InlineKeyboardButton(text="🔙 Volver", callback_data="admin_content_missions")])
    await callback.message.edit_text(
        "Selecciona la misión a eliminar:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_mission_"))
async def admin_confirm_delete_mission(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    mission_id = callback.data.split("delete_mission_")[-1]
    mission = await session.get(Mission, mission_id)
    if not mission:
        await callback.answer("Misión no encontrada", show_alert=True)
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Confirmar", callback_data=f"confirm_delete_{mission_id}")],
            [InlineKeyboardButton(text="🔙 Cancelar", callback_data="admin_delete_mission")],
        ]
    )
    await callback.message.edit_text(
        f"¿Eliminar misión {mission.name}?",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_"))
async def admin_delete_mission(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    mission_id = callback.data.split("confirm_delete_")[-1]
    service = MissionService(session)
    await service.delete_mission(mission_id)
    await callback.message.edit_text(
        "❌ Misión eliminada",
        reply_markup=get_admin_content_missions_keyboard(),
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

