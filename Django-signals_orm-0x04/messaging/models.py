import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class Message(models.Model):
    """Model to represent user-to-user messages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # ✅ track if message was edited
    edited_at = models.DateTimeField(null=True, blank=True)  # ✅ timestamp of last edit
    is_deleted = models.BooleanField(default=False)  # ✅ soft delete flag
    deleted_at = models.DateTimeField(null=True, blank=True)  # ✅ timestamp of deletion

    # Custom manager
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager

    def _str_(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"

class Notification(models.Model):
    """Model to represent notifications for messages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def _str_(self):
        return f"Notification for {self.user.username}: {self.message.content[:20]}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="history")
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(   # ✅ NEW
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    def _str_(self):
        return f"History of message {self.message.id} at {self.edited_at}"

class Conversation(models.Model):
    """Conversation between participants"""
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    """Message model supporting threaded replies"""
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    # ✅ self-referential field for threading
    parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE
    )

    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="edited_messages",
        on_delete=models.SET_NULL
    )

    def _str_(self):
        return f"{self.sender.username}: {self.message_body[:30]}"

    def get_thread(self):
        """
        ✅ Recursive function to fetch all replies in a threaded format
        """
        replies = self.replies.all().select_related("sender").prefetch_related("replies")
        thread = []
        for reply in replies:
            thread.append({
                "id": reply.id,
                "sender": reply.sender.username,
                "message_body": reply.message_body,
                "sent_at": reply.sent_at,
                "replies": reply.get_thread(),  # recursive
            })
        return thread
    

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    """Custom manager to get unread messages for a specific user."""

    def unread_for_user(self, user):
        # ✅ Retrieve only necessary fields to optimize performance
        return self.filter(receiver=user, read=False).only("id", "message_body", "sender", "sent_at")


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    parent_message = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    read = models.BooleanField(default=False)  # ✅ Added field to track read status

    # ✅ Custom managers
    objects = models.Manager()  # default
    unread = UnreadMessagesManager()  # custom unread manager

    def _str_(self):
        return f"Message from {self.sender} to {self.receiver}"

    def mark_as_read(self):
        """Mark the message as read."""
        self.read = True
        self.save()

from django.db import models
from django.contrib.auth import get_user_model
from .managers import UnreadMessagesManager

User = get_user_model()

