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
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ["participants__username"]

    def get_queryset(self):
        """
        ✅ Users should only see conversations they are part of
        """
        return Conversation.objects.filter(participants=self.request.user)

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
        """Ensure creator is part of the conversation"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Messages"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ["sender_first_name", "sender_last_name", "message_body"]

    def get_queryset(self):
        """
        ✅ Ensure users only see messages from conversations they participate in
        """
        return Message.objects.filter(conversation__participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation
        """
        conversation_id = request.data.get("conversation")
        message_body = request.data.get("message_body")

        conversation = get_object_or_404(Conversation, pk=conversation_id)

        # ✅ Check participant access
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "You are not allowed to send messages in this conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )

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

        # ✅ Ensure only participants can view
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "You are not allowed to view this conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        messages = conversation.messages.all().order_by("sent_at")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


def index(request):
    return JsonResponse({"message": "Messaging app API is running 🚀"})