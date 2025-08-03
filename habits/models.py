from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    linked_habit = models.ForeignKey('self', null=True, blank=True,
                                     on_delete=models.SET_NULL, limit_choices_to={'is_pleasant': True})
    frequency = models.PositiveSmallIntegerField(default=1)  # в днях
    reward = models.CharField(max_length=255, blank=True, null=True)
    duration = models.PositiveSmallIntegerField(help_text="Время выполнения в секундах")
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.action} в {self.place} ({self.time})"
