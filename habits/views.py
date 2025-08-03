from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnly


class HabitPagination(PageNumberPagination):
    """Пагинация по 5 привычек на страницу."""
    page_size = 5


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD привычек с учётом прав доступа и пагинации.
    """
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = HabitPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['action', 'place']

    def get_queryset(self):
        """Переопределяем, чтобы возвращать только свои привычки (кроме публичных)."""
        user = self.request.user
        if self.action == "list":
            # Только свои привычки
            return Habit.objects.filter(user=user)
        return Habit.objects.all()

    def perform_create(self, serializer):
        """Автоматически подставляем текущего пользователя как владельца привычки."""
        serializer.save(user=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet только для просмотра публичных привычек.
    """
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = HabitPagination
