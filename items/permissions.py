from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only the owner of an item can edit or delete it.
    Anyone can view (GET requests).
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only allowed to the owner
        return obj.owner == request.user