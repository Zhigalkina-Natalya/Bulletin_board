from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from advertisements.models import Category
from users.models import User
from users.serializers import ChangePasswordSerializer


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
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="123456")


class UserSerializerTestCase(APITestCase):
    """Тесты сериализаторов пользователей"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="123456")
        self.factory = APIRequestFactory()

    def test_change_password_serializer_valid(self):
        """Проверка корректной смены пароля через сериализатор"""
        request = self.factory.post("/")
        request.user = self.user

        serializer = ChangePasswordSerializer(
            data={"old_password": "123456", "new_password": "Newpass123!"},
            context={"request": type("Req", (), {"user": self.user})()},
        )
        self.assertTrue(serializer.is_valid())

    def test_change_password_serializer_invalid_old(self):
        serializer = ChangePasswordSerializer(
            data={"old_password": "wrong", "new_password": "abcdef"},
            context={"request": type("Req", (), {"user": self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    def test_change_password_serializer_short_new(self):
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


class UserViewsTestCase(APITestCase):
    """Тесты views пользователей"""

    def setUp(self):
        self.user = User.objects.create_user(email="test2@example.com", password="123456")
        self.client.force_authenticate(user=self.user)

    def test_change_password_view_success(self):
        """Смена пароля успешна"""
        url = reverse("users:change_password")
        response = self.client.post(url, {"old_password": "123456", "new_password": "Newpass123!"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Newpass123!"))

    def test_change_password_view_wrong_old(self):
        url = reverse("users:change_password")
        response = self.client.post(url, {"old_password": "wrong", "new_password": "abcdef"})
        self.assertEqual(response.status_code, 400)

    def test_profile_view_get(self):
        url = reverse("users:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)

    def test_profile_view_update(self):
        url = reverse("users:profile")
        response = self.client.patch(url, {"phone": "+7123456789", "city": "Москва"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+7123456789")
        self.assertEqual(self.user.city, "Москва")

    def test_profile_unauthorized(self):
        self.client.force_authenticate(user=None)

        url = reverse("users:profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_register_user(self):
        url = reverse("users:register")

        response = self.client.post(url, {"email": "new@test.com", "password": "123456"})

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())


class ManagementCommandsTestCase(TestCase):
    def test_create_groups_command(self):
        call_command("create_groups")
        self.assertTrue(Group.objects.filter(name="Content Manager").exists())


class CreateAdminCommandTestCase(TestCase):
    """Тест команды createadmin"""

    @patch("builtins.input", side_effect=["admin@example.com", "123456"])
    def test_createadmin_command(self, mock_input):
        from django.core.management import call_command

        call_command("createadmin")
        from users.models import User

        self.assertTrue(User.objects.filter(email="admin@example.com").exists())

    def test_create_admin_command(self):
        out = StringIO()
        call_command("createadmin", stdout=out)

        self.assertIn("Администратор", out.getvalue())

    def test_create_admin_already_exists(self):
        email = "testadmin@example.com"
        password = "SafePassword123!"

        # Сначала создаём администратора вручную
        User.objects.create_superuser(email=email, password=password)

        out = StringIO()

        # Мокаем input() так, чтобы команда пыталась создать того же админа
        with patch("builtins.input", side_effect=[email, password]):
            call_command("createadmin", stdout=out)

        # Проверяем, что админ не был создан заново
        self.assertEqual(User.objects.filter(email=email).count(), 1)

        # Проверяем, что вывод команды содержит предупреждение
        self.assertIn("уже существует", out.getvalue())


class CreateGroupsCommandTestCase(TestCase):
    """Тест команды create_groups"""

    def test_create_groups_command(self):
        """Проверка создания группы Content Manager"""
        call_command("create_groups")

        self.assertTrue(Group.objects.filter(name="Content Manager").exists())

    def test_create_groups_idempotent(self):
        """Команда не создает дубликаты"""
        call_command("create_groups")
        call_command("create_groups")

        self.assertEqual(Group.objects.filter(name="Content Manager").count(), 1)


class AdditionalUserTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="123456")

    def test_user_str(self):
        """Проверка __str__ пользователя"""
        self.assertEqual(str(self.user), "user@test.com")

    def test_profile_requires_auth(self):
        """Профиль требует авторизации"""
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 401)

    def test_change_password_invalid_new(self):
        """Слабый пароль не проходит"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("users:change_password"), {"old_password": "123456", "new_password": "123"}
        )

        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_email(self):
        """Нельзя зарегистрировать одинаковый email"""
        response = self.client.post(reverse("users:register"), {"email": "user@test.com", "password": "123456"})

        self.assertEqual(response.status_code, 400)


class UserViewExtraTestCase(APITestCase):
    """Дополнительные тесты для users.views"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="123456")

    def test_profile_unauthorized(self):
        url = reverse("users:profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_change_password_unauthorized(self):
        url = reverse("users:change_password")

        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 401)


class CategoryViewTestCase(APITestCase):
    """Тесты для категорий"""

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_category_list_public(self):
        """Список категорий доступен всем"""
        response = self.client.get("/api/advertisements/categories/")
        self.assertEqual(response.status_code, 200)

    def test_category_create_only_admin(self):
        """Создавать категории может только админ"""
        response = self.client.post("/api/advertisements/categories/", {"name": "New Category"})
        self.assertEqual(response.status_code, 401)

    def test_category_create_as_admin(self):
        from users.models import User

        admin = User.objects.create_superuser(email="admin@test.com", password="123456")
        self.client.force_authenticate(user=admin)

        response = self.client.post("/api/advertisements/categories/", {"name": "Admin Category"})

        self.assertEqual(response.status_code, 201)
