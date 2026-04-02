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
            title="Тест объявление",
            description="Описание",
            price=1000,
            author=self.user,
            category=self.category
        )

    def test_get_ads_list(self):
        url = reverse("advertisements:ad-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("advertisements.tasks.notify_new_ad.delay")
    def test_create_ad(self, mock_notify):
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-list")

        data = {
            "title": "Новое объявление",
            "description": "Описание",
            "price": 2000,
            "category": self.category.id
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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

    def test_search(self):
        url = reverse("advertisements:ad-list") + "?search=Тест"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ordering(self):
        url = reverse("advertisements:ad-list") + "?ordering=price"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_ad(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-detail", args=[self.ad.id])

        data = {
            "title": "Обновлено",
            "description": "Описание",
            "price": 1500,
            "category": self.category.id
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionTestCase(APITestCase):
    """Тесты для проверки прав доступа"""

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user1 = User.objects.create_user(email="user1@test.com", password="123456")
        self.user2 = User.objects.create_user(email="user2@test.com", password="123456")

        self.category = Category.objects.create(name="Тест")

        self.ad = Ad.objects.create(
            title="Объявление",
            description="Описание",
            price=1000,
            author=self.user1,
            category=self.category
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


class TaskTestCase(APITestCase):
    """Тестирование Celery задач"""

    @patch("builtins.print")
    def test_notify_new_ad(self, mock_print):
        from advertisements.tasks import notify_new_ad
        notify_new_ad("Тестовое объявление")
        mock_print.assert_called_once_with("Новое объявление создано: Тестовое объявление")  # 🟢 новый тест
