from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение: безопасные методы (GET, HEAD, OPTIONS) доступны всем,
    изменение и удаление — только автору объекта."""
    
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
