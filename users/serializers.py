from django.contrib.auth.password_validation import validate_password
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

    username_field = User.EMAIL_FIELD


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

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
        """Валидация нового пароля через системную проверку Django"""
        validate_password(value)
        return value
