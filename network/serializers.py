from rest_framework import serializers

from .models import Node, Product


class ProductSerializer(serializers.ModelSerializer):
    """Серилизатор для модели Product. Отображает все поля модели."""

    class Meta:
        model = Product
        fields = "__all__"


class NodeSerializer(serializers.ModelSerializer):
    """Серилизатор для модели Node.
    Включает дополнительное поле 'supplier_detail' — строковое описание поставщика.
    Поле 'products' — отображает связанные продукты (ReadOnly).
    Поля, не предназначенные для редактирования (например, created_at) — в readonly."""

    # Связь с другим узлом (поставщиком)
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Node.objects.all(), required=False, allow_null=True
    )
    # Связанные продукты — читаемое поле
    products = ProductSerializer(many=True, read_only=True)
    # Получение более понятного описания поставщика
    supplier_detail = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            "id",
            "name",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "supplier",
            "supplier_detail",
            "debt",
            "created_at",
            "products",
        ]
        read_only_fields = ("created_at", "debt")

    def validate_supplier(self, value):
        """Валидирует поле supplier. Значение поля supplier (объект Node или None)."""
        if value == self.instance:
            raise serializers.ValidationError("Поставщик не может быть самим собой.")
        return value

    @staticmethod
    def get_supplier_detail(obj):
        """Возвращает строку с информацией о поставщике."""
        return str(obj.supplier) if obj.supplier else None
