from django.contrib import admin
from django.utils.html import format_html

from .models import Ad, Category


class AdInline(admin.TabularInline):
    """Inline объявления внутри категории."""

    model = Ad
    extra = 0


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Админка объявлений с превью картинки."""

    list_display = ("id", "title", "image_preview", "price", "author", "category", "is_active")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("image_preview",)
    ordering = ("-created_at",)

    def image_preview(self, obj):
        """Показывает миниатюру изображения."""
        if obj.image and hasattr(obj.image, "url"):
            return format_html('<img src="{}" width="70" height="50" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = "Изображение"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий + inline объявления."""

    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [AdInline]
