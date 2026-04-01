from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей с превью аватарки."""

    model = User

    list_display = ("id", "email", "avatar_preview", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональные данные", {"fields": ("phone", "city", "avatar")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2"), },),)

    def avatar_preview(self, obj):
        """Показывает миниатюру аватарки."""
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
        return "Нет аватара"

    avatar_preview.short_description = "Аватар"
