import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# IDs hardcoded for demonstration. Replace with database or persistent storage.
ADMIN_IDS = {123456789}  # Reemplaza con el ID real del administrador
VIP_USERS = {987654321}  # Reemplaza con IDs de usuarios VIP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        reply_text = "\u2728 Men\u00fa de Administrador \u2728"
        keyboard = [["Estad\u00edsticas"], ["Gestionar VIPs"]]
    elif user_id in VIP_USERS:
        reply_text = "\ud83c\udf81 Men\u00fa VIP \ud83c\udf81"
        keyboard = [["Jugar"], ["Mi Progreso"]]
    else:
        reply_text = "\ud83d\udc65 Men\u00fa de Suscripci\u00f3n \ud83d\udc65"
        keyboard = [["Suscribirme"], ["Info del Canal"]]

    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(reply_text, reply_markup=markup)


def main() -> None:
    # Coloca tu token de bot aqu\u00ed
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
