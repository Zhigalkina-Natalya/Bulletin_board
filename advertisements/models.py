from django.conf import settings
from django.db import models


class Category(models.Model):
    """Модель категории объявлений. Позволяет группировать объявления по типу (например: авто, недвижимость)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название",
        help_text="Введите название категории",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ad(models.Model):
    """Модель объявления. Содержит основную информацию о товаре, услуге."""

    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
        help_text="Введите название объявления",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Введите описание объявления",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Укажите цену",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        help_text="Укажите автора объявления",
        related_name="ads",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="ads",
        verbose_name="Категория",
        help_text="Выберите категорию",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Отображается ли объявление",
    )

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
