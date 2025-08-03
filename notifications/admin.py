from django.contrib import admin
from .models import TelegramProfile


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "chat_id")
    search_fields = ("user__username", "chat_id")
