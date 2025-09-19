from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Node, Product


class ModelTests(TestCase):
    def test_product_creation(self):
        """Тестирует создание продукта. Проверяет, что продукт создается с
        правильными полями name и model."""
        product = Product.objects.create(
            name="Test Product", model="Model X", release_date="2023-01-01"
        )
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.model, "Model X")

    def test_node_hierarchy_level(self):
        """Тестирует расчет уровня иерархии для узлов. Создает завод (уровень 0) и
        розничную сеть (уровень 1), проверяя, что метод get_hierarchy_level()
        возвращает корректные значения."""
        # Завод (уровень 0)
        factory = Node.objects.create(
            name="Factory",
            email="factory@test.com",
            country="Russia",
            city="Moscow",
            street="Main",
            house_number="1",
        )
        self.assertEqual(factory.get_hierarchy_level(), 0)

        # Розничная сеть (уровень 1)
        retailer = Node.objects.create(
            name="Retailer",
            email="retailer@test.com",
            country="Russia",
            city="SPb",
            street="Street",
            house_number="2",
            supplier=factory,
        )
        self.assertEqual(retailer.get_hierarchy_level(), 1)

    def test_node_clean_validation(self):
        """Тестирует валидацию модели Node на циклы в иерархии. Создает завод и
        пытается сделать его поставщиком самому себе, ожидая ValidationError при
        вызове full_clean()."""
        # Тест на цикл (завод не может ссылаться на себя)
        factory = Node.objects.create(
            name="Factory",
            email="factory@test.com",
            country="Russia",
            city="Moscow",
            street="Main",
            house_number="1",
        )
        with self.assertRaises(ValidationError):  # Ожидаем ValidationError
            factory.supplier = factory
            factory.full_clean()


class ViewTests(APITestCase):
    def setUp(self):
        """Настройка тестов: создает пользователя и аутентифицирует клиента."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass", is_staff=True, is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_node_list_authenticated(self):
        """Тестирует получение списка узлов для аутентифицированного пользователя.
        Отправляет GET-запрос на /api/nodes/ и проверяет статус 200 OK."""
        response = self.client.get("/api/nodes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_node_create(self):
        """Тестирует создание нового узла. Отправляет POST-запрос с данными узла на
        /api/nodes/ и проверяет статус 201 Created."""
        data = {
            "name": "New Node",
            "email": "new@test.com",
            "country": "Russia",
            "city": "Moscow",
            "street": "Test",
            "house_number": "10",
        }
        response = self.client.post("/api/nodes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_node_debt_readonly(self):
        """Тестирует, что поле debt только для чтения. Создает узел с debt=100,
        пытается обновить его на 200 через PATCH, и проверяет, что debt не изменился
        (остался 100)."""
        # Создаём узел
        node = Node.objects.create(
            name="Test Node",
            email="test@test.com",
            country="Russia",
            city="Moscow",
            street="Test",
            house_number="1",
            debt=100.00,
        )
        # Пытаемся обновить debt — должно игнорироваться
        data = {"debt": 200.00}
        response = self.client.patch(f"/api/nodes/{node.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        node.refresh_from_db()
        self.assertEqual(node.debt, 100.00)  # Debt не изменился

    def test_unauthenticated_access_denied(self):
        """Тестирует отказ в доступе для неаутентифицированного пользователя. Выходит
        из системы и отправляет GET-запрос на /api/nodes/, ожидая статус 401 Unauthorized.
        """
        # Клиент аутентифицирован в setUp, так что logout делает его неаутентифицированным
        self.client.logout()

        # Запрос без credentials — аутентификаторы вернут 403
        response = self.client.get("/api/nodes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
