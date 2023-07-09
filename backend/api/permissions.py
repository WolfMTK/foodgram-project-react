from rest_framework import permissions


class IsAuthorPermission(permissions.BasePermission):
    """Разрешение только автору."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author and request.user.is_authenticated
