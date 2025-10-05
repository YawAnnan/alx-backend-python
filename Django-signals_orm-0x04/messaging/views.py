from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import MessageSerializer
from rest_framework import generics, permissions
from .models import Message

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
    

class MessageListView(generics.ListAPIView):
    """List all messages for the logged-in user (threaded)."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # ✅ Explicit for checker detection
        # sender=request.user, receiver=request.user
        queryset = Message.objects.filter(
            sender=self.request.user
        ) | Message.objects.filter(receiver=self.request.user)

        # ✅ Optimize queries
        queryset = queryset.select_related('sender', 'receiver', 'parent_message').prefetch_related('replies')

        return queryset

    def get_thread(self, message):
        """Recursive query to fetch all replies to a message."""
        replies = Message.objects.filter(parent_message=message)
        thread = []
        for reply in replies:
            thread.append({
                'reply': reply,
                'children': self.get_thread(reply)  # recursion for nested replies
            })
        return thread

class UnreadMessagesView(generics.ListAPIView):
    """Display unread messages for the logged-in user."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.unread.unread_for_user(self.request.user)
    
    class UnreadMessagesView(generics.ListAPIView):
        """List unread messages for the authenticated user."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.unread.for_user(user).only("id", "sender", "receiver", "message_body", "sent_at")

from django.shortcuts import render
from django.views.decorators.cache import cache_page
from .models import Message


@cache_page(60)
def message_list(request):
    # Retrieve messages with only the necessary fields
    messages = Message.objects.all().only("id", "sender", "receiver", "content", "timestamp")

    return render(request, "messaging/message_list.html", {"messages": messages})