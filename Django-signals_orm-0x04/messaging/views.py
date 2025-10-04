from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import MessageSerializer

User = get_user_model()


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    Allow an authenticated user to delete their account.
    """
    user = request.user
    username = user.username
    user.delete()
    return Response(
        {"detail": f"User {username} and related data deleted successfully."},
        status=status.HTTP_204_NO_CONTENT
    )



class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related("sender", "parent_message").prefetch_related("replies")
    serializer_class = MessageSerializer

    @action(detail=True, methods=["get"])
    def thread(self, request, pk=None):
        """
        ✅ Get a message and its entire threaded conversation
        """
        message = get_object_or_404(Message, pk=pk)
        data = {
            "id": message.id,
            "sender": message.sender.username,
            "message_body": message.message_body,
            "sent_at": message.sent_at,
            "replies": message.get_thread(),
        }
        return Response(data, status=status.HTTP_200_OK)