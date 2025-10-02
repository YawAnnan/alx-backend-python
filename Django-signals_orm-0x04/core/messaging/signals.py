from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from messaging.models import Message, Notification, MessageHistory
from django.db.models.signals import post_delete
from django.contrib.auth import get_user_model

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
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                    edited_by=instance.sender  # ✅ Track who edited
            )
            instance.edited = True
        except Message.DoesNotExist:
            pass
    

User = get_user_model()


@receiver(post_delete, sender=User)
def delete_related_data(sender, instance, **kwargs):
    """
    Clean up all user-related data when a User is deleted.
    """
    # Delete messages where user is sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete notifications belonging to the user
    Notification.objects.filter(user=instance).delete()

    # Delete message histories where edited_by is the user
    MessageHistory.objects.filter(edited_by=instance).delete()