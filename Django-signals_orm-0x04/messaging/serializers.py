# messaging/serializers.py

from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "message_body",
            "sent_at",
            "parent_message",
            "edited",
            "edited_by",
        ]