from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from advertisements.models import Ad, Category
from advertisements.permissions import IsOwnerOrReadOnly
from users.models import User


class AdTestCase(APITestCase):
    """Тесты для модели объявлений и API."""

    def setUp(self):
        """Создаем пользователя и категорию"""
        self.user = User.objects.create_user(email="test@example.com", password="123456")

        self.category = Category.objects.create(name="Недвижимость")

        self.ad = Ad.objects.create(
            title="Тест объявление", description="Описание", price=1000, author=self.user, category=self.category
        )

    def test_get_ads_list(self):
        """Проверка получения списка объявлений"""
        url = reverse("advertisements:ad-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_ad(self):
        """Проверка создания объявления"""
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-list")

        data = {"title": "Новое объявление", "description": "Описание", "price": 2000, "category": self.category.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_ad_only_owner(self):
        """Удаление доступно только автору"""
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-detail", args=[self.ad.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_ad_unauthorized(self):
        """Удаление без авторизации запрещено"""
        url = reverse("advertisements:ad-detail", args=[self.ad.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_price(self):
        """Фильтр по цене"""
        url = reverse("advertisements:ad-list") + "?min_price=500&max_price=1500"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_ad(self):
        """Обновление объявления"""
        self.client.force_authenticate(user=self.user)

        url = reverse("advertisements:ad-detail", args=[self.ad.id])

        data = {"title": "Обновлено", "description": "Описание", "price": 1500, "category": self.category.id}

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
            title="Объявление", description="Описание", price=1000, author=self.user1, category=self.category
        )

    def test_owner_can_edit(self):
        """Владелец может редактировать"""
        request = self.factory.put("/")
        request.user = self.user1

        permission = IsOwnerOrReadOnly()

        self.assertTrue(permission.has_object_permission(request, None, self.ad))

    def test_non_owner_cannot_edit(self):
        """Не владелец не может редактировать"""
        request = self.factory.put("/")
        request.user = self.user2

        permission = IsOwnerOrReadOnly()

        self.assertFalse(permission.has_object_permission(request, None, self.ad))

    def test_safe_method_allowed(self):
        """GET разрешен всем"""
        request = self.factory.get("/")
        request.user = self.user2

        permission = IsOwnerOrReadOnly()

        self.assertTrue(permission.has_object_permission(request, None, self.ad))
