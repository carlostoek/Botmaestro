import os
from typing import List

# Obtain the Telegram bot token from the ``BOT_TOKEN`` environment
# variable. This avoids hard coding sensitive information in the
# source code. If the variable is missing or still set to the
# placeholder value, raise an explicit error so the user knows what to
# do.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")

if BOT_TOKEN == "YOUR_BOT_TOKEN" or not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN environment variable is not set or contains the default placeholder."
    )

# Telegram user IDs of admins provided as a semicolon separated list in
# the ``ADMIN_IDS`` environment variable. Falling back to an empty
# list keeps the bot running even if no admins are configured.
ADMIN_IDS: List[int] = [
    int(uid) for uid in os.environ.get("ADMIN_IDS", "").split(";") if uid.strip()
]

# Telegram user IDs with a VIP subscription. This is helpful for
# testing without relying on channel membership. The IDs should be
# provided through the ``VIP_IDS`` environment variable separated by
# semicolons.
VIP_IDS: List[int] = [
    int(uid) for uid in os.environ.get("VIP_IDS", "").split(";") if uid.strip()
]

# Identifier of the VIP channel where subscribers are checked. This
# must be set via the ``VIP_CHANNEL_ID`` environment variable. A value
# of ``0`` disables VIP checks and treats all users as non‑VIP.
VIP_CHANNEL_ID = int(os.environ.get("VIP_CHANNEL_ID", "0"))

# ID of the free Telegram channel used for basic access. A value of ``0``
# disables handling of free channel join requests.
FREE_CHANNEL_ID = int(os.environ.get("FREE_CHANNEL_ID", "0"))

class Config:
    BOT_TOKEN = BOT_TOKEN
    ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else 0
    CHANNEL_ID = VIP_CHANNEL_ID
    FREE_CHANNEL_ID = FREE_CHANNEL_ID
    VIP_IDS = VIP_IDS
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///gamification.db")
