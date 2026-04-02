from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "city",
            "avatar",
        ]
        read_only_fields = ["email"]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для получения JWT токена по email."""

    username_field = "email"


class UserRegisterSerializer(serializers.ModelSerializer):
    """Регистрация пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """Проверка старого пароля."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль введен неверно")
        return value

    def validate_new_password(self, value):
        """Можно добавить валидацию сложности пароля, указав количество символов."""
        if len(value) < 5:
            raise serializers.ValidationError("Пароль должен быть не менее 5 символов")
        return value
