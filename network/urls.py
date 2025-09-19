from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NodeViewSet, ProductViewSet

# Создаем роутер — автоматическая генерация URL для ViewSet
router = DefaultRouter()
router.register(r"nodes", NodeViewSet)
router.register(r"products", ProductViewSet)

urlpatterns = [
    # Включаем маршруты API
    path("", include(router.urls)),
]
