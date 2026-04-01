from rest_framework import serializers

from .models import Ad, Category


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = "__all__"


class AdSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ad. Обрабатывает создание, обновление и отображение объявлений."""

    author = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = Ad
        fields = [
            "id",
            "title",
            "description",
            "image",
            "price",
            "author",
            "category",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["author"]
