from collections import defaultdict
from typing import Dict, List

from aiogram.fsm.state import State, StatesGroup

# Simple in-memory stack of admin menu states per user
_user_states: Dict[int, List[str]] = defaultdict(list)


def reset_state(user_id: int) -> None:
    """Initialize the state stack for an admin user."""
    _user_states[user_id] = ["main"]


def push_state(user_id: int, state: str) -> None:
    """Push a new state onto the user's stack if it isn't the current one."""
    stack = _user_states.setdefault(user_id, ["main"])
    if not stack or stack[-1] != state:
        stack.append(state)


def pop_state(user_id: int) -> str:
    """Pop the current state and return the new one."""
    stack = _user_states.get(user_id, ["main"])
    if stack:
        stack.pop()
    if not stack:
        stack.append("main")
    return stack[-1]


def current_state(user_id: int) -> str:
    """Return the current state for the user."""
    stack = _user_states.get(user_id, ["main"])
    return stack[-1]


class AdminTariffStates(StatesGroup):
    """States for the admin tariff configuration flow."""

    waiting_for_tariff_duration = State()
    waiting_for_tariff_price = State()
    waiting_for_tariff_name = State()


class AdminUserStates(StatesGroup):
    """States for admin user management actions."""

    assigning_points_amount = State()
    search_user_query = State()


class AdminContentStates(StatesGroup):
    """States related to posting content to channels."""

    waiting_for_channel_post_text = State()


class AdminConfigStates(StatesGroup):
    """States for bot configuration options."""

    waiting_for_reaction_buttons = State()
    waiting_for_channel_interval = State()
    waiting_for_vip_interval = State()


class AdminVipMessageStates(StatesGroup):
    """States for configuring VIP channel messages."""

    waiting_for_reminder_message = State()
    waiting_for_farewell_message = State()


class AdminMissionStates(StatesGroup):
    """States for creating missions from the admin panel."""

    creating_mission_name = State()
    creating_mission_description = State()
    creating_mission_points = State()
    creating_mission_type = State()
    creating_mission_requires_action = State()
    creating_mission_action_data = State()


class AdminDailyGiftStates(StatesGroup):
    """States for configuring the daily gift."""

    waiting_for_amount = State()


class AdminEventStates(StatesGroup):
    creating_event_name = State()
    creating_event_description = State()
    creating_event_multiplier = State()


class AdminRaffleStates(StatesGroup):
    creating_raffle_name = State()
    creating_raffle_description = State()
    creating_raffle_prize = State()


class AdminRewardStates(StatesGroup):
    """States for creating rewards from the admin panel."""

    creating_reward_name = State()
    creating_reward_description = State()
    creating_reward_cost = State()
    creating_reward_stock = State()
