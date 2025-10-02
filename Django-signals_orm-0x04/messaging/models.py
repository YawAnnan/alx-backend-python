import uuid
from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """Model to represent user-to-user messages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # ✅ track if message was edited
    '''edited_at = models.DateTimeField(null=True, blank=True)  # ✅ timestamp of last edit
    is_deleted = models.BooleanField(default=False)  # ✅ soft delete flag
    deleted_at = models.DateTimeField(null=True, blank=True)  # ✅ timestamp of deletion'''

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

    def _str_(self):
        return f"History of message {self.message.id} at {self.edited_at}"