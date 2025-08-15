# flake8: noqa: E402
import sys
import os
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habits_project.settings')
django.setup()


from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from notifications.models import TelegramProfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habits_project.settings')
django.setup()


User = get_user_model()


@sync_to_async
def get_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


@sync_to_async
def link_chat_id(user, chat_id):
    TelegramProfile.objects.update_or_create(
        user=user, defaults={'chat_id': chat_id}
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Привязывает Telegram chat_id к пользователю по username."""
    chat_id = update.effective_chat.id
    if context.args:
        username = context.args[0]
        user = await get_user(username)
        if user:
            await link_chat_id(user, chat_id)
            await update.message.reply_text(
                f"Привет, {username}! Chat_id успешно привязан."
            )
        else:
            await update.message.reply_text("Пользователь не найден.")
    else:
        await update.message.reply_text("Отправь /start <твой username на сайте>")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
