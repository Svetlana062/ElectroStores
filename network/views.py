from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.permissions import IsAuthenticated

from .models import Node, Product
from .pagination import StandardResultsSetPagination
from .permissions import IsActiveEmployee
from .serializers import NodeSerializer, ProductSerializer


class NodeViewSet(viewsets.ModelViewSet):
    """API для работы с узлами сети. Реализует стандартные CRUD-операции.
    Описание фильтров и поиска для удобства."""

    queryset = Node.objects.all()
    serializer_class = NodeSerializer

    # Аутентификация
    authentication_classes = [
        SessionAuthentication,
        TokenAuthentication,
        BasicAuthentication,
    ]

    # Фильтры и поиск по API
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["name", "city"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    # Права доступа
    permission_classes = [IsAuthenticated, IsActiveEmployee]


class ProductViewSet(viewsets.ModelViewSet):
    """API для работы с продуктами. Стандартные CRUD операции. Можно искать и сортировать."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Аутентификация
    authentication_classes = [
        SessionAuthentication,
        TokenAuthentication,
        BasicAuthentication,
    ]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "model"]
    ordering_fields = ["release_date"]

    # Права доступа
    permission_classes = [IsAuthenticated, IsActiveEmployee]
