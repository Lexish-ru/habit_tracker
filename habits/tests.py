
from django.test import TestCase
from django.contrib.auth import get_user_model
from habits.models import Habit
from rest_framework.test import APITestCase
from habits.serializers import HabitSerializer
from rest_framework.test import APIClient

User = get_user_model()


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="12:00",
            action="Выпить чай",
            is_pleasant=True,
            frequency=1,
            duration=60,
            is_public=True
        )

    def test_create_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            place="Улица",
            time="13:00",
            action="Погулять",
            frequency=1,
            duration=90,
        )
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.place, "Улица")
        self.assertFalse(habit.is_pleasant)

    def test_str(self):
        self.assertIn(self.user.username, str(self.pleasant_habit))


class HabitSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user2", password="testpass2")
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Ванна",
            time="15:00",
            action="Принять ванну",
            is_pleasant=True,
            frequency=1,
            duration=80,
        )

    def test_reward_and_linked_habit(self):
        data = {
            "user": self.user.id,
            "place": "Дом",
            "time": "16:00",
            "action": "Читать книгу",
            "frequency": 1,
            "duration": 60,
            "reward": "Чай",
            "linked_habit": self.pleasant_habit.id
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Нельзя одновременно указывать 'reward' и 'linked_habit'.", str(serializer.errors))

    def test_duration_over_120(self):
        data = {
            "user": self.user.id,
            "place": "Дом",
            "time": "16:00",
            "action": "Уборка",
            "frequency": 1,
            "duration": 130,
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Время выполнения не может быть больше 120 секунд.", str(serializer.errors))

    def test_frequency_too_low(self):
        data = {
            "user": self.user.id,
            "place": "Дом",
            "time": "16:00",
            "action": "Медитация",
            "frequency": 0,
            "duration": 60,
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Периодичность должна быть от 1 до 7 дней.", str(serializer.errors))

    def test_pleasant_with_reward(self):
        data = {
            "user": self.user.id,
            "place": "Ванна",
            "time": "17:00",
            "action": "Принять ванну",
            "is_pleasant": True,
            "frequency": 1,
            "duration": 70,
            "reward": "Шоколад",
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("У приятной привычки не может "
                      "быть ни вознаграждения, ни связанной привычки.", str(serializer.errors))


class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="apipass")
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Ванна",
            time="14:00",
            action="SPA",
            is_pleasant=True,
            frequency=1,
            duration=50,
            is_public=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_habit(self):
        data = {
            "place": "Парк",
            "time": "19:00",
            "action": "Бег",
            "frequency": 2,
            "duration": 40
        }
        response = self.client.post('/api/habits/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['place'], "Парк")

    def test_pagination(self):
        # Создаем 6 привычек
        for i in range(6):
            Habit.objects.create(
                user=self.user,
                place=f"Место{i}",
                time="08:00",
                action=f"Действие{i}",
                frequency=1,
                duration=60
            )
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIn('next', response.data)

    def test_only_owner_can_edit(self):
        user2 = User.objects.create_user(username="another", password="pass")
        habit = Habit.objects.create(
            user=user2, place="Где-то", time="10:00", action="Чужое", frequency=1, duration=50
        )
        response = self.client.patch(f'/api/habits/{habit.id}/', {"place": "Новое"})
        self.assertEqual(response.status_code, 403)  # Нет доступа к чужой привычке

    def test_public_habits(self):
        response = self.client.get('/api/public-habits/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['results']), 1)
