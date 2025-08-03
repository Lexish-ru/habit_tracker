from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Доступ разрешён только владельцу объекта.
    Публичные привычки разрешены для чтения всем.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем читать публичные привычки
        if request.method in SAFE_METHODS and obj.is_public:
            return True
        # Полный доступ — только владельцу
        return obj.user == request.user
