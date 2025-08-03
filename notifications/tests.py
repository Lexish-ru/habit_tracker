from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import TelegramProfile
from notifications.tasks import send_telegram_reminder, check_and_send_habit_reminders
from unittest import mock
from habits.models import Habit
from datetime import datetime

User = get_user_model()


class TelegramProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tguser", password="123456")
        self.chat_id = 123456789

    def test_create_telegram_profile(self):
        profile = TelegramProfile.objects.create(user=self.user, chat_id=self.chat_id)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.chat_id, self.chat_id)
        self.assertIn(self.user.username, str(profile))

    def test_chat_id_unique(self):
        TelegramProfile.objects.create(user=self.user, chat_id=self.chat_id)
        user2 = User.objects.create_user(username="tguser2", password="654321")
        with self.assertRaises(Exception):
            TelegramProfile.objects.create(user=user2, chat_id=self.chat_id)

    def test_one_to_one_constraint(self):
        TelegramProfile.objects.create(user=self.user, chat_id=self.chat_id)
        with self.assertRaises(Exception):
            TelegramProfile.objects.create(user=self.user, chat_id=999999999)


class SendTelegramReminderTaskTest(TestCase):
    @mock.patch("notifications.tasks.Bot")
    def test_send_telegram_reminder(self, mock_bot_class):
        mock_bot = mock.Mock()
        mock_bot_class.return_value = mock_bot

        chat_id = 111222333
        message = "Test reminder"
        send_telegram_reminder(chat_id, message)

        mock_bot.send_message.assert_called_once_with(chat_id=chat_id, text=message)


class CheckAndSendHabitRemindersTaskTest(TestCase):
    @mock.patch("notifications.tasks.send_telegram_reminder.delay")
    def test_check_and_send_habit_reminders(self, mock_send_telegram_reminder_delay):
        # Создаем пользователя и профиль Telegram
        user = User.objects.create_user(username="reminder_user", password="testpass")
        chat_id = 555666777
        TelegramProfile.objects.create(user=user, chat_id=chat_id)

        # Устанавливаем время привычки на сейчас (секунды и микросекунды обнуляем для совпадения)
        now = datetime.now().replace(second=0, microsecond=0)
        now_time_str = now.time().strftime('%H:%M:%S')
        # Создаём привычку, которую надо напомнить
        Habit.objects.create(
            user=user,
            place="Дом",
            time=now_time_str,
            action="Полить цветы",
            frequency=1,
            duration=30,
        )
        # Вызываем таску
        check_and_send_habit_reminders()

        # Проверяем, что отправка напоминания была вызвана
        mock_send_telegram_reminder_delay.assert_called_once()
        called_args, called_kwargs = mock_send_telegram_reminder_delay.call_args
        self.assertEqual(called_args[0], chat_id)
        self.assertIn("Полить цветы", called_args[1])

    @mock.patch("notifications.tasks.send_telegram_reminder.delay")
    def test_check_and_send_habit_reminders_no_profile(self, mock_send_telegram_reminder_delay):
        # Привычка без Telegram-профиля не вызывает отправку напоминания
        user = User.objects.create_user(username="no_profile", password="testpass")
        now = datetime.now().replace(second=0, microsecond=0)
        now_time_str = now.time().strftime('%H:%M:%S')
        Habit.objects.create(
            user=user,
            place="Дом",
            time=now_time_str,
            action="Почистить зубы",
            frequency=1,
            duration=20,
        )
        check_and_send_habit_reminders()
        mock_send_telegram_reminder_delay.assert_not_called()
