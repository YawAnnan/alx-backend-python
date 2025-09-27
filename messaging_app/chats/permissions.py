from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission: only allow users to access their own objects.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming your message/conversation model has a `user` field
        return obj.user == request.user
   