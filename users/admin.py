from django.contrib import admin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для пользователей с превью аватарки."""

    list_display = ("id", "email", "avatar_preview", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("id",)

    def avatar_preview(self, obj):
        """Показывает миниатюру аватарки."""
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
        return "Нет аватара"

    avatar_preview.short_description = "Аватар"
