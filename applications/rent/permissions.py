from rest_framework import permissions

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Allows access to the object owner or staff user.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.owner == request.user
