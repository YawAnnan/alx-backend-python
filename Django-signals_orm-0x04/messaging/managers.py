from django.db import models

class UnreadMessagesManager(models.Manager):
    """Custom manager to filter unread messages for a specific user."""
    def for_user(self, user):
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .only("id", "sender", "receiver", "message_body", "sent_at")
        )