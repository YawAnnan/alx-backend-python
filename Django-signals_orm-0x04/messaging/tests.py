from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class SignalTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="alice", password="password")
        self.receiver = User.objects.create_user(username="bob", password="password")

    def test_notification_created_on_message(self):
        """Ensure a notification is created when a message is sent"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )

        # Check notification exists
        notification = Notification.objects.filter(user=self.receiver, message=message).first()
        self.assertIsNotNone(notification)
        self.assertFalse(notification.is_read)