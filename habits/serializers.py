from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit с реализацией всех бизнес-валидаторов.
    """

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Habit
        fields = '__all__'

    def validate(self, data):
        """
        Валидация данных привычки по всем бизнес-правилам.
        """

        reward = data.get('reward')
        linked_habit = data.get('linked_habit')
        is_pleasant = data.get('is_pleasant', False)
        duration = data.get('duration')
        frequency = data.get('frequency', 1)

        if reward and linked_habit:
            raise serializers.ValidationError(
                "Нельзя одновременно указывать 'reward' и 'linked_habit'."
            )
        if duration and duration > 120:
            raise serializers.ValidationError(
                "Время выполнения не может быть больше 120 секунд."
            )
        if linked_habit and not linked_habit.is_pleasant:
            raise serializers.ValidationError(
                "В связанное поле можно выбирать только привычку с признаком 'приятная'."
            )
        if is_pleasant and (reward or linked_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть ни вознаграждения, ни связанной привычки."
            )
        if frequency < 1 or frequency > 7:
            raise serializers.ValidationError(
                "Периодичность должна быть от 1 до 7 дней."
            )
        return data
