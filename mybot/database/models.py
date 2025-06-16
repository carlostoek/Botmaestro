# database/models.py
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, JSON, Text, ForeignKey, Float
from uuid import uuid4
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.future import select

Base = declarative_base()

class User(AsyncAttrs, Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, unique=True) # Telegram User ID
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    points = Column(Float, default=0)
    level = Column(Integer, default=1)
    achievements = Column(JSON, default={}) # {'achievement_id': timestamp_isoformat}
    missions_completed = Column(JSON, default={}) # {'mission_id': timestamp_isoformat}
    # Track last reset for daily/weekly missions
    last_daily_mission_reset = Column(DateTime, default=func.now())
    last_weekly_mission_reset = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Role management and VIP expiration
    role = Column(String, default="free")
    vip_expires_at = Column(DateTime, nullable=True)
    last_reminder_sent_at = Column(DateTime, nullable=True)
    
    # ¡NUEVA COLUMNA para el estado del menú!
    menu_state = Column(String, default="root") # e.g., "root", "profile", "missions", "rewards"

    # ¡NUEVA COLUMNA para registrar reacciones a mensajes del canal!
    # Guarda un diccionario donde la clave es el message_id del canal y el valor es un booleano (True)
    # o el timestamp de la reacción para futura expansión si necesitamos historial.
    # Por ahora, un simple booleano es suficiente para registrar si el usuario ya reaccionó a ese mensaje.
    channel_reactions = Column(JSON, default={}) # {'message_id': True}

class Reward(AsyncAttrs, Base):
    __tablename__ = "rewards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    cost = Column(Integer, default=0)
    stock = Column(Integer, default=-1) # -1 for unlimited
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class Achievement(AsyncAttrs, Base):
    __tablename__ = "achievements"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    condition_type = Column(String, nullable=False)
    condition_value = Column(Integer, nullable=False)
    reward_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())


class UserAchievement(AsyncAttrs, Base):
    __tablename__ = "user_achievements"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    achievement_id = Column(String, ForeignKey("achievements.id"), primary_key=True)
    unlocked_at = Column(DateTime, default=func.now())

class Mission(AsyncAttrs, Base):
    __tablename__ = "missions"
    id = Column(String, primary_key=True, unique=True) # e.g., 'daily_login', 'event_trivia_challenge'
    name = Column(String, nullable=False)
    description = Column(Text)
    points_reward = Column(Integer, default=0)
    type = Column(String, default="one_time") # 'daily', 'weekly', 'one_time', 'event', 'reaction'
    is_active = Column(Boolean, default=True)
    requires_action = Column(Boolean, default=False) # True if requires a specific button click/action outside the bot's menu
    # action_data puede ser usado para especificar, por ejemplo, qué 'button_id' de reacción completa la misión
    action_data = Column(JSON, nullable=True) # e.g., {'button_id': 'like_post_1'} or {'target_message_id': 12345}
    created_at = Column(DateTime, default=func.now())

class Event(AsyncAttrs, Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    multiplier = Column(Integer, default=1) # e.g., 2 for double points
    is_active = Column(Boolean, default=True)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Raffle(AsyncAttrs, Base):
    __tablename__ = "raffles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    prize = Column(String, nullable=True)
    winner_id = Column(BigInteger, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)


class RaffleEntry(AsyncAttrs, Base):
    __tablename__ = "raffle_entries"
    raffle_id = Column(Integer, ForeignKey("raffles.id"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime, default=func.now())


class Level(AsyncAttrs, Base):
    __tablename__ = "levels"

    level_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    min_points = Column(Integer, nullable=False)
    reward = Column(String, nullable=True)


class VipSubscription(AsyncAttrs, Base):
    __tablename__ = "vip_subscriptions"
    user_id = Column(BigInteger, primary_key=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class UserProgress(AsyncAttrs, Base):
    __tablename__ = "user_progress"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    total_points = Column(Float, default=0)
    last_activity_at = Column(DateTime, default=func.now())
    last_checkin_at = Column(DateTime, nullable=True)
    last_daily_gift_at = Column(DateTime, nullable=True)
    last_notified_points = Column(Float, default=0)
    messages_sent = Column(Integer, default=0)
    checkin_streak = Column(Integer, default=0)


class InviteToken(AsyncAttrs, Base):
    __tablename__ = "invite_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False)
    created_by = Column(BigInteger, nullable=False)
    used_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=func.now())
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)


class SubscriptionPlan(AsyncAttrs, Base):
    __tablename__ = "subscription_plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    status = Column(String, default="available")
    created_by = Column(BigInteger, nullable=False)
    used_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=func.now())
    used_at = Column(DateTime, nullable=True)


class SubscriptionToken(AsyncAttrs, Base):
    __tablename__ = "subscription_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False)
    plan_id = Column(Integer, nullable=False)
    created_by = Column(BigInteger, nullable=False)
    used_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=func.now())
    used_at = Column(DateTime, nullable=True)


class Token(AsyncAttrs, Base):
    """VIP activation tokens linked to tariffs."""

    __tablename__ = "tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    token_string = Column(String, unique=True)
    tariff_id = Column(Integer, ForeignKey("tariffs.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    generated_at = Column(DateTime, default=func.now())
    activated_at = Column(DateTime, nullable=True)
    is_used = Column(Boolean, default=False)


class Tariff(AsyncAttrs, Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    duration_days = Column(Integer)
    price = Column(Integer)


class ConfigEntry(AsyncAttrs, Base):
    __tablename__ = "config_entries"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)


class BotConfig(AsyncAttrs, Base):
    __tablename__ = "bot_config"
    id = Column(Integer, primary_key=True, autoincrement=True)
    free_channel_wait_time_minutes = Column(Integer, default=0)


class Channel(AsyncAttrs, Base):
    __tablename__ = "channels"
    id = Column(BigInteger, primary_key=True)  # Telegram chat ID
    title = Column(String, nullable=True)



class PendingChannelRequest(AsyncAttrs, Base):
    __tablename__ = "pending_channel_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    request_timestamp = Column(DateTime, default=func.now())
    approved = Column(Boolean, default=False)


class Challenge(AsyncAttrs, Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # daily, weekly, monthly
    goal_type = Column(String, nullable=False)  # messages, reactions, checkins
    goal_value = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)


class UserChallengeProgress(AsyncAttrs, Base):
    __tablename__ = "user_challenge_progress"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), primary_key=True)
    current_value = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)


# Funciones para manejar el estado del menú del usuario
async def get_user_menu_state(session, user_id: int) -> str:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and user.menu_state:
        return user.menu_state
    return "root"

async def set_user_menu_state(session, user_id: int, state: str):
    user = await session.get(User, user_id)
    if user:
        user.menu_state = state
        await session.commit()
        await session.refresh(user)

