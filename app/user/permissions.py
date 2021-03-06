from rest_framework import permissions
from django.contrib.auth import get_user_model


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to super admin users. """
    message = "Only Super Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.roles and request.user.roles == 'SUPERADMIN')


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users. """
    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.roles and request.user.roles == 'ADMIN')


class IsRegularUser(permissions.BasePermission):
    """Allows access only to talent users. """
    message = "Only Regular users are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.roles and  request.user.roles == 'REGULAR')
