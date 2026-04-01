from rest_framework.routers import DefaultRouter

from .views import AdViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r"ads", AdViewSet)
router.register(r"categories", CategoryViewSet)

urlpatterns = []

urlpatterns += router.urls
