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

# Telegram user IDs of admins
ADMIN_IDS: List[int] = [123456789]

# Telegram user IDs of VIP subscribers
VIP_IDS: List[int] = [987654321]
