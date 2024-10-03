from rest_framework.permissions import BasePermission


class IsCollector(BasePermission):
    """
    Разрешение для доступа только сборщикам.
    """
    def has_permission(self, request, view):
        # Проверяем, что пользователь аутентифицирован и его роль — 'collector'
        return request.user.is_authenticated and request.user.role == 'collector' or request.user.role == 'delivery'


# class IsCourier(BasePermission):
#     """
#     Разрешение для доступа только delivery.
#     """
#     def has_permission(self, request, view):
#         # Проверяем, что пользователь аутентифицирован и его роль — 'delivery'
#         return request.user.is_authenticated and request.user.role == 'delivery'
