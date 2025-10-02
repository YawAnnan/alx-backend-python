from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from messaging.models import Message, Notification, MessageHistory

# ✅ Signal 1: Notify receiver when a new message is created
@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )


# ✅ Signal 2: Log edits when a message is updated
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:  # Only if the message already exists
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                # Save history before update
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass