from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """Модель для представления продукта в сети.
    Продукты могут быть связаны с несколькими узлами сети (звеньями) через
    ManyToMany связь, что позволяет гибко управлять ассортиментом (например,
    один продукт может поставляться нескольким звеньям)."""

    name = models.CharField(
        max_length=255,
        verbose_name="Название продукта",
        help_text="Название товара, например 'Смартфон Samsung'.",
    )
    model = models.CharField(
        max_length=255,
        verbose_name="Модель",
        help_text="Модель товара, например 'Galaxy S21'.",
    )
    release_date = models.DateField(
        verbose_name="Дата выхода на рынок", help_text="Когда продукт был выпущен."
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]

    def __str__(self):
        """Строковое представление продукта: "Название - Модель"."""
        return f"{self.name} - {self.model}"


class Node(models.Model):
    """Модель для представления звена сети (узла). Представляет иерархическую структуру:
    завод (уровень 0), розничная сеть и индивидуальный предприниматель. Каждое звено (кроме
    завода) ссылается на одного поставщика оборудования (не обязательно предыдущего по
    иерархии). Уровень определяется расстоянием до завода по цепочке поставщиков."""

    name = models.CharField("Название", max_length=255)
    email = models.EmailField("Email")
    country = models.CharField("Страна", max_length=100)
    city = models.CharField("Город", max_length=100)
    street = models.CharField("Улица", max_length=255)
    house_number = models.CharField("Номер дома", max_length=50)
    supplier = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Поставщик",
        help_text="Ссылка на поставщика. Для завода оставьте пустым.",
    )
    debt = models.DecimalField(
        "Задолженность", max_digits=12, decimal_places=2, default=0
    )
    created_at = models.DateTimeField("Время создания", auto_now_add=True)
    products = models.ManyToManyField(Product, verbose_name="Продукты", blank=True)

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"
        ordering = ["name"]

    def __str__(self):
        """Строковое представление звена."""
        return self.name

    def clean(self):
        """Валидация модели Node:
        - Проверка на циклы в иерархии поставщиков.
        - Проверка уровней: уровень поставщика должен быть ниже уровня текущего узла."""
        if self.supplier:
            supplier_level = self.supplier.get_hierarchy_level()
            self_level = self.get_hierarchy_level()

            # Исправление: Добавлена проверка на None перед сравнением
            if (
                supplier_level is not None
                and self_level is not None
                and supplier_level >= self_level
            ):
                raise ValidationError(
                    _("Уровень поставщика должен быть ниже уровня текущего узла."),
                    code="invalid_hierarchy_level",
                )

        # Проверка на циклы в иерархии
        visited = set()
        current = self
        while current:
            if current in visited:
                raise ValidationError(
                    _("Обнаружен цикл в иерархии поставщиков."), code="hierarchy_cycle"
                )
            visited.add(current)
            current = current.supplier

    def get_hierarchy_level(self):
        """
        Возвращает уровень в иерархии на основе цепочки поставщиков.

        Завод всегда уровень 0 (если supplier=None). Для остальных — минимальное расстояние до завода по supplier.
        Если цепочка оборвана (нет пути к заводу) или цикл, возвращает None.
        """
        if self.supplier is None:
            return 0  # Завод
        level = 0
        current = self.supplier
        visited = set()  # Защита от циклов
        while current:
            if current.id in visited:
                return None  # Цикл — ошибка
            visited.add(current.id)
            level += 1
            if current.supplier is None:  # Дошли до завода
                return level
            current = current.supplier
        return None  # Нет пути к заводу
