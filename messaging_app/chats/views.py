from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversations"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "participants__username",
        "participants__first_name",
        "participants__last_name",
    ]
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

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
        """Automatically add the current user to conversation participants"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Messages"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["sender_username", "senderfirst_name", "sender_last_name", "message_body"]
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation
        """
        conversation_id = request.data.get("conversation")
        message_body = request.data.get("message_body")

        if not (conversation_id and message_body):
            return Response(
                {"error": "conversation and message_body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = get_object_or_404(Conversation, pk=conversation_id)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_body=message_body,
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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