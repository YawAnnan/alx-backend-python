from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission: only allow users to access their own objects.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming your message/conversation model has a `user` field
        return obj.user == request.user

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:
    - Only allow authenticated users
    - Only participants of a conversation can send, view, update, or delete messages
    """

    def has_permission(self, request, view):
        # First check: user must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Case 1: object is a Conversation
        if hasattr(obj, "participants"):
            return request.user in obj.participants.all()

        # Case 2: object is a Message
        if hasattr(obj, "conversation"):
            return request.user in obj.conversation.participants.all()

        return False