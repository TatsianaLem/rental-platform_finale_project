from rest_framework import permissions
from applications.user.choices.roles import UserRole

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Allows all authorized to read. Change - only to the owner or staff.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.is_staff

class IsLandlordOrReadOnly(permissions.BasePermission):
    """
    Only LANDLORD can change data, the rest can only read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.LANDLORD.name
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsBookingParticipant(permissions.BasePermission):
    """
    Only the tenant can create and the participants (tenant or landlord) can display.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated and request.user.role == UserRole.TENANT.name
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.tenant or request.user == obj.rent.owner