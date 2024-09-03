from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Custom permission to allow only admins to create, update, or delete products.
    All authenticated users can view products.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Otherwise, only allow admins
        return request.user and request.user.is_staff


class IsAdminUserOrOwner(BasePermission):
    """
    Custom permission to only allow admins or the owner of the order to view their own order.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user