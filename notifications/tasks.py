import os
from celery import shared_task
from telegram import Bot
from datetime import datetime
from habits.models import Habit


@shared_task
def send_telegram_reminder(chat_id: int, message: str) -> None:
    """
    Отправляет сообщение в Telegram пользователю по chat_id.
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    bot = Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)


@shared_task
def check_and_send_habit_reminders():
    """
    Проверяет привычки, которые нужно выполнить сейчас,
    и отправляет напоминания пользователям.
    """
    now = datetime.now().time().replace(second=0, microsecond=0)
    habits = Habit.objects.filter(time=now)
    for habit in habits:
        tg_profile = getattr(habit.user, 'telegram_profile', None)
        if tg_profile:
            message = f'Напоминание: {habit.action} в {habit.place}!'
            send_telegram_reminder.delay(tg_profile.chat_id, message)
