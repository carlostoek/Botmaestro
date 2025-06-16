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
   export FREE_CHANNEL_ID="-100987654321" # ID of the free Telegram channel
   export VIP_IDS="33333;44444"        # optional list of VIP user IDs
   ```

3. Run the bot:

   ```bash
   python mybot/bot.py
   ```

## Project structure

All active source code lives under the `mybot/` package. An earlier
`old_gamificacion` folder containing a legacy prototype has been removed
to avoid confusion.
