from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Единое правило администратора"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class IsOwnerOrManagerOrReadOnly(BasePermission):
    """Разрешение:
    - SAFE методы - могут все
    - Автор может свое редактировать
    - Контент-менеджер может редактировать всё
    - Админ может всё
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return (
            obj.author == user
            or user.groups.filter(name="Content Manager").exists()
            or user.is_staff
            or user.is_superuser
        )


class IsContentManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="Content Manager").exists()


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff
