from django.http import JsonResponse
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer




class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversations"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]   # ✅ use filters
    search_fields = ['participants__first_name', 'participants__last_name']
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants
        """
        participants = request.data.get("participants", [])
        if not participants or len(participants) < 2:
            return Response(
                {"error": "At least two participants are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def perform_create(self, serializer):
        """Create a new conversation"""
        serializer.save()


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Messages"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter]   # ✅ use filters
    search_fields = ['sender__first_name', 'sender__last_name', 'message_body']

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation
        """
        conversation_id = request.data.get("conversation")
        message_body = request.data.get("message_body")
        sender_id = request.data.get("sender")

        if not (conversation_id and message_body and sender_id):
            return Response(
                {"error": "conversation, sender, and message_body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = get_object_or_404(Conversation, pk=conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender_id=sender_id,
            message_body=message_body,
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """Send a new message to a conversation"""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=["get"])
    def by_conversation(self, request, pk=None):
        """
        Custom endpoint to get all messages in a conversation
        """
        conversation = get_object_or_404(Conversation, pk=pk)
        messages = conversation.messages.all().order_by("sent_at")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


def index(request):
    return JsonResponse({"message": "Messaging app API is running 🚀"})
