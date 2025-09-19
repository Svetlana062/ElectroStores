from django.contrib import admin

from .models import Node, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Product. Отображает имя, модель и дату релиза.
    Позволяет искать по имени и модели, фильтровать по дате релиза."""

    list_display = ("name", "model", "release_date")
    search_fields = ("name", "model")
    list_filter = ("release_date",)


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Node. Отображает основные поля, фильтрует по
    городу и стране. Добавлено пользовательское действие для очистки задолженности."""

    list_display = (
        "name",
        "email",
        "country",
        "city",
        "street",
        "house_number",
        "supplier",
        "debt",
        "created_at",
    )
    list_filter = ("city", "country")
    search_fields = ("name", "city")
    actions = ["clear_debt"]
    readonly_fields = ("created_at", "debt")
    ordering = ("name",)

    def clear_debt(self, request, queryset):
        """Пользовательское админское действие. Устанавливает задолженность выбранных узлов в 0."""
        updated_count = queryset.update(debt=0)
        self.message_user(
            request, f"{updated_count} узлов успешно очищены задолженности."
        )

    clear_debt.short_description = (
        "Очистить задолженность перед поставщиком у выбранных узлов."
    )
