from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserTestCase(APITestCase):
    """Тесты для пользователей и JWT."""

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="123456")

    def test_create_user(self):
        """Проверка создания пользователя"""
        self.assertEqual(User.objects.count(), 1)

    def test_jwt_token(self):
        """Получение JWT токена"""
        url = reverse("token_obtain_pair")

        data = {"email": "test@example.com", "password": "123456"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_jwt_wrong_password(self):
        """Неверный пароль"""
        url = reverse("token_obtain_pair")

        data = {"email": "test@example.com", "password": "wrong"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserModelTestCase(TestCase):
    """Тесты модели пользователя"""

    def test_create_user(self):
        """Создание пользователя"""
        user = User.objects.create_user(email="user1@test.com", password="123456")

        self.assertEqual(user.email, "user1@test.com")
        self.assertTrue(user.check_password("123456"))

    def test_create_superuser(self):
        """Создание суперпользователя"""
        user = User.objects.create_superuser(email="admin@test.com", password="123456")

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_str_method(self):
        """Проверка __str__"""
        user = User.objects.create_user(email="user2@test.com", password="123456")

        self.assertEqual(str(user), "user2@test.com")

    def test_email_required(self):
        """Email обязателен"""
        with self.assertRaises(TypeError):
            User.objects.create_user(password="123456")
