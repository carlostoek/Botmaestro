# Botmaestro

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Export your Telegram bot token in the `BOT_TOKEN` environment variable and
   configure optional role variables:

   ```bash
   export BOT_TOKEN="<your_bot_token>"
   export ADMIN_IDS="11111;22222"       # user IDs with admin privileges
   export VIP_CHANNEL_ID="-100123456789"  # ID of the VIP Telegram channel
   export VIP_IDS=""                   # optional semicolon-separated list of user IDs treated as VIP
   ```

3. Run the bot:

   ```bash
   python mybot/bot.py
   ```
