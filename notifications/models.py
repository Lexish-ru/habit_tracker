from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TelegramProfile(models.Model):
    """
    Хранит связь пользователя и его Telegram chat_id.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    chat_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return f'{self.user.username} (chat_id: {self.chat_id})'
