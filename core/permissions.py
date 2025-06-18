from rest_framework.permissions import BasePermission


class BlockAll(BasePermission):
    def has_permission(self, request, view):
        return False
