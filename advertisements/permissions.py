from rest_framework.permissions import BasePermission


class IsOwnerOrManagerOrReadOnly(BasePermission):
    """Разрешение:
    - Читать могут все
    - Автор может свое редактировать
    - Контент-менеджер может редактировать всё
    - Админ может всё
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # админ
        if request.user.is_superuser:
            return True

        # контент-менеджер
        if request.user.groups.filter(name="Content Manager").exists():
            return True

        # автор
        return obj.author == request.user
