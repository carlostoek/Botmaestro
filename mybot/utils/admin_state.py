from collections import defaultdict
from typing import Dict, List

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
