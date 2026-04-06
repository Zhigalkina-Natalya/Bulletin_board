from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from .models import Ad, Category
from .pagination import AdPagination
from .permissions import IsAdmin, IsOwnerOrManagerOrReadOnly
from .serializers import AdSerializer, CategorySerializer
from .tasks import notify_new_ad


class CategoryViewSet(ModelViewSet):
    """
    ViewSet для работы с категориями. Позволяет:
    - получать список категорий
    - создавать новые категории
    - редактировать и удалять категории
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.request.user.groups.filter(name="Content Manager").exists():
            return [IsAuthenticated()]

        return [IsAdmin()]


class AdFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Ad
        fields = ["category"]


class AdViewSet(ModelViewSet):
    """
    ViewSet для работы с объявлениями. Позволяет:
    - создавать объявления
    - просматривать список
    - редактировать и удалять (только автору)
    """

    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrManagerOrReadOnly]
    pagination_class = AdPagination

    # фильтрация + поиск + сортировка
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = AdFilter

    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]

    search_fields = ["title", "description"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user

        # неавторизованные - только активные
        if not user.is_authenticated:
            return Ad.objects.filter(is_active=True)

        # админ - видит всё
        if user.is_staff or user.is_superuser:
            return Ad.objects.all()

        # менеджер - видит всё
        if user.groups.filter(name="Content Manager").exists():
            return Ad.objects.all()

        # автор: свои + активные чужие
        return Ad.objects.filter(Q(is_active=True) | Q(author=user))

    def perform_create(self, serializer):
        """Автоматически устанавливает автора объявления."""
        ad = serializer.save(author=self.request.user)
        notify_new_ad.delay(ad.title)
