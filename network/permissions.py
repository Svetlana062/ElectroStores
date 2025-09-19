from rest_framework.permissions import BasePermission


class IsActiveEmployee(BasePermission):
    """Разрешает доступ только аутентифицированным активным сотрудникам (is_staff=True и is_active=True)."""

    message = "Доступ разрешен только активным сотрудникам."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active  # Пользователь активен
            and request.user.is_staff  # Пользователь — сотрудник (админ/персонал)
        )
