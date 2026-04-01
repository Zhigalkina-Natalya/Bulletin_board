from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.viewsets import ModelViewSet

from .models import Ad, Category
from .permissions import IsOwnerOrReadOnly
from .serializers import AdSerializer, CategorySerializer


class CategoryViewSet(ModelViewSet):
    """
    ViewSet для работы с категориями. Позволяет:
    - получать список категорий
    - создавать новые категории
    - редактировать и удалять категории
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]


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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = AdFilter

    def perform_create(self, serializer):
        """Автоматически устанавливает автора объявления."""
        serializer.save(author=self.request.user)
