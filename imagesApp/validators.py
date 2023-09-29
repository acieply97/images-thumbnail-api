from rest_framework import permissions


class IsOwnerOrAdminImage(permissions.BasePermission):
    """
        Show Image only for image owner and administrator
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsOwnerOrAdminThumbnail(permissions.BasePermission):
    """
        Show Thumbnail only for thumbnail owner and administrator
    """
    def has_object_permission(self, request, view, obj):
        return obj.image.user == request.user or request.user.is_staff
