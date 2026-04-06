from unittest.mock import patch

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from advertisements.models import Ad, Category
from advertisements.permissions import IsOwnerOrManagerOrReadOnly
from users.models import User


class AdTestCase(APITestCase):
    """Тесты для модели объявлений и API."""

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="123456")
        self.other_user = User.objects.create_user(email="other@test.com", password="123456")

        self.category = Category.objects.create(name="Недвижимость")

        self.ad = Ad.objects.create(
            title="Тест объявление", description="Описание", price=1000, author=self.user, category=self.category
        )

    def test_get_ads_list(self):
        url = reverse("advertisements:ad-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    @patch("advertisements.tasks.notify_new_ad.delay")
    def test_create_ad(self, mock_notify):
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-list")

        data = {"title": "Новое объявление", "description": "Описание", "price": 2000, "category": self.category.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.user.email)
        mock_notify.assert_called_once()  # проверяем celery

    def test_delete_ad_only_owner(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-detail", args=[self.ad.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_ad_unauthorized(self):
        url = reverse("advertisements:ad-detail", args=[self.ad.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_ad_not_owner(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse("advertisements:ad-detail", args=[self.ad.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_price(self):
        url = reverse("advertisements:ad-list") + "?min_price=500&max_price=1500"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_search(self):
        url = reverse("advertisements:ad-list") + "?search=Тест"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_ordering(self):
        url = reverse("advertisements:ad-list") + "?ordering=price"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["results"][0]["price"]), 1000)

    def test_inactive_ads_hidden(self):
        Ad.objects.create(
            title="Скрытое", description="...", price=100, author=self.user, category=self.category, is_active=False
        )

        response = self.client.get(reverse("advertisements:ad-list"))

        self.assertEqual(len(response.data["results"]), 1)

    def test_update_ad(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-detail", args=[self.ad.id])

        data = {"title": "Обновлено", "description": "Описание", "price": 1500, "category": self.category.id}

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Обновлено")

    def test_user_sees_only_active_ads(self):
        self.client.force_authenticate(user=self.other_user)

        Ad.objects.create(
            title="Неактивное", description="...", price=500, author=self.user, category=self.category, is_active=False
        )

        response = self.client.get(reverse("advertisements:ad-list"))

        for ad in response.data["results"]:
            self.assertTrue(ad["is_active"])


class PermissionTestCase(APITestCase):
    """Тесты для проверки прав доступа"""

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user1 = User.objects.create_user(email="user1@test.com", password="123456")
        self.user2 = User.objects.create_user(email="user2@test.com", password="123456")

        self.category = Category.objects.create(name="Тест")

        self.ad = Ad.objects.create(
            title="Объявление", description="Описание", price=1000, author=self.user1, category=self.category
        )

        # добавили группу Content Manager
        self.manager_group = Group.objects.create(name="Content Manager")
        self.user2.groups.add(self.manager_group)

    def test_owner_can_edit(self):
        request = self.factory.put("/")
        request.user = self.user1

        permission = IsOwnerOrManagerOrReadOnly()

        self.assertTrue(permission.has_object_permission(request, None, self.ad))

    def test_manager_can_edit(self):
        request = self.factory.put("/")
        request.user = self.user2

        permission = IsOwnerOrManagerOrReadOnly()

        self.assertTrue(permission.has_object_permission(request, None, self.ad))

    def test_non_owner_cannot_edit(self):
        self.user2.groups.clear()  # убрали роль менеджера

        request = self.factory.put("/")
        request.user = self.user2

        permission = IsOwnerOrManagerOrReadOnly()

        self.assertFalse(permission.has_object_permission(request, None, self.ad))

    def test_safe_method_allowed(self):
        request = self.factory.get("/")
        request.user = self.user2

        permission = IsOwnerOrManagerOrReadOnly()

        self.assertTrue(permission.has_object_permission(request, None, self.ad))

    def test_admin_can_edit(self):
        admin = User.objects.create_user(email="admin@test.com", password="123456", is_staff=True)

        request = self.factory.put("/")
        request.user = admin

        permission = IsOwnerOrManagerOrReadOnly()

        self.assertTrue(permission.has_object_permission(request, None, self.ad))


class TaskTestCase(APITestCase):
    """Тестирование Celery задач"""

    @patch("builtins.print")
    def test_notify_new_ad(self, mock_print):
        from advertisements.tasks import notify_new_ad

        notify_new_ad("Тестовое объявление")
        mock_print.assert_called_once_with("Новое объявление создано: Тестовое объявление")


class AdditionalAdTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="123456")
        self.admin = User.objects.create_user(email="admin@test.com", password="123456", is_staff=True)

        self.category = Category.objects.create(name="Авто")

        self.ad = Ad.objects.create(
            title="BMW", description="Машина", price=1000, author=self.user, category=self.category
        )

    def test_admin_sees_all_ads(self):
        """Админ видит все объявления (включая неактивные)"""
        self.client.force_authenticate(user=self.admin)

        Ad.objects.create(
            title="Скрытое", description="...", price=500, author=self.user, category=self.category, is_active=False
        )

        response = self.client.get(reverse("advertisements:ad-list"))

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data["results"]), 2)

    def test_category_str(self):
        """Проверка __str__ категории"""
        self.assertEqual(str(self.category), "Авто")

    def test_ad_str(self):
        """Проверка __str__ объявления"""
        self.assertEqual(str(self.ad), "BMW")

    def test_permission_safe_method(self):
        """SAFE метод разрешен всем"""
        permission = IsOwnerOrManagerOrReadOnly()
        request = APIRequestFactory().get("/")
        request.user = self.user

        self.assertTrue(permission.has_object_permission(request, None, self.ad))

    def test_permission_denied_for_random_user(self):
        """Чужой пользователь не может редактировать"""
        other = User.objects.create_user(email="other@test.com", password="123456")

        permission = IsOwnerOrManagerOrReadOnly()
        request = APIRequestFactory().put("/")
        request.user = other

        self.assertFalse(permission.has_object_permission(request, None, self.ad))


class AdViewExtraTestCase(APITestCase):
    """Дополнительные тесты для покрытия views"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="123456")
        self.admin = User.objects.create_user(
            email="admin@test.com", password="123456", is_staff=True, is_superuser=True
        )

        self.category = Category.objects.create(name="Тест")

        self.active_ad = Ad.objects.create(
            title="Активное", description="...", price=100, author=self.user, category=self.category, is_active=True
        )

        self.inactive_ad = Ad.objects.create(
            title="Неактивное", description="...", price=200, author=self.user, category=self.category, is_active=False
        )

    def test_create_ad_unauthorized(self):
        """Нельзя создать без авторизации"""
        url = reverse("advertisements:ad-list")

        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 401)

    def test_partial_update(self):
        """PATCH обновление"""
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-detail", args=[self.active_ad.id])

        response = self.client.patch(url, {"price": 999})

        self.assertEqual(response.status_code, 200)
        self.active_ad.refresh_from_db()
        self.assertEqual(self.active_ad.price, 999)
