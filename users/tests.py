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


class UserSerializerTestCase(APITestCase):
    """Тесты сериализаторов пользователей"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="123456")

    def test_change_password_serializer_valid(self):
        from users.serializers import ChangePasswordSerializer

        serializer = ChangePasswordSerializer(
            data={"old_password": "123456", "new_password": "abcdef"},
            context={"request": type("Req", (), {"user": self.user})()},
        )
        self.assertTrue(serializer.is_valid())

    def test_change_password_serializer_invalid_old(self):
        from users.serializers import ChangePasswordSerializer

        serializer = ChangePasswordSerializer(
            data={"old_password": "wrong", "new_password": "abcdef"},
            context={"request": type("Req", (), {"user": self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    def test_change_password_serializer_short_new(self):
        from users.serializers import ChangePasswordSerializer

        serializer = ChangePasswordSerializer(
            data={"old_password": "123456", "new_password": "123"},
            context={"request": type("Req", (), {"user": self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)

    def test_user_register_serializer(self):
        from users.serializers import UserRegisterSerializer

        data = {"email": "new@example.com", "password": "123456"}
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, "new@example.com")


#
# class UserViewsTestCase(APITestCase):
#     """Тесты views пользователей"""
#
#     def setUp(self):
#         self.user = User.objects.create_user(email="test2@example.com", password="123456")
#         self.client.force_authenticate(user=self.user)
#
#     def test_change_password_view_success(self):
#         from django.urls import reverse
#         url = reverse("change_password")
#         response = self.client.post(url, {"old_password": "123456", "new_password": "abcdef"})
#         self.assertEqual(response.status_code, 200)
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.check_password("abcdef"))
#
#     def test_change_password_view_wrong_old(self):
#         from django.urls import reverse
#         url = reverse("change_password")
#         response = self.client.post(url, {"old_password": "wrong", "new_password": "abcdef"})
#         self.assertEqual(response.status_code, 400)
#
#     def test_profile_view_get(self):
#         from django.urls import reverse
#         url = reverse("profile")
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["email"], self.user.email)
#
#     def test_profile_view_update(self):
#         from django.urls import reverse
#         url = reverse("profile")
#         response = self.client.put(url, {"phone": "+7123456789", "city": "Москва"})
#         self.assertEqual(response.status_code, 200)
#         self.user.refresh_from_db()
#         self.assertEqual(self.user.phone, "+7123456789")
#         self.assertEqual(self.user.city, "Москва")
