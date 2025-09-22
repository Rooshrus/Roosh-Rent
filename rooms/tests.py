from django.test import TestCase, Client
from django.urls import reverse
from .models import Room
import json

class RoomModelTest(TestCase):
    def setUp(self):
        # Створюємо тестову кімнату
        self.room = Room.objects.create(
            username="Тестовий Користувач",
            price=100.50,
            address="вул. Тестова, 1",
            coordX=49.8419,
            coordY=24.0315,
            picture="https://example.com/test.jpg"
        )

    def test_room_creation(self):
        """Перевіряє, чи кімната коректно створюється в базі даних."""
        self.assertEqual(self.room.username, "Тестовий Користувач")
        self.assertEqual(float(self.room.price), 100.50)
        self.assertTrue(isinstance(self.room, Room))

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.room = Room.objects.create(
            username="Тестовий Користувач",
            price=200.00,
            address="вул. Тестова, 2",
            coordX=50.4501,
            coordY=30.5234
        )

    def test_rooms_page_status_code(self):
        """Перевіряє, чи сторінка /rooms/ повертає код 200."""
        response = self.client.get(reverse('rooms'))
        self.assertEqual(response.status_code, 200)

    def test_add_room_page_status_code(self):
        """Перевіряє, чи сторінка /addroom/ повертає код 200."""
        response = self.client.get(reverse('add_room'))
        self.assertEqual(response.status_code, 200)

    def test_rooms_api_returns_json(self):
        """Перевіряє, чи API /roomsapi/ повертає коректний JSON."""
        response = self.client.get(reverse('roomsApi'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data[0]['username'], "Тестовий Користувач")

    def test_add_room_post_request(self):
        """Перевіряє, чи POST-запит на /addroom/ додає кімнату."""
        response = self.client.post(reverse('add_room'), {
            'username': 'Новий Користувач',
            'price': 300.00,
            'address': 'вул. Нова, 3',
            'coordX': 51.5074,
            'coordY': -0.1278,
            'csrfmiddlewaretoken': 'testtoken'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Room.objects.filter(username='Новий Користувач').exists())

class APITest(TestCase):
    def test_empty_api_response(self):
        """Перевіряє, чи API повертає пустий список, якщо кімнат немає."""
        response = self.client.get(reverse('roomsApi'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])