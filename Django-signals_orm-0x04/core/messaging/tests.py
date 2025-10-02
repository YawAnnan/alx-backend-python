from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Message, Notification, MessageHistory

User = get_user_model()


class DeleteUserSignalTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")

        # Log in as user1
        self.client.login(username="alice", password="password123")

        # Create a message
        self.message = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Hello Bob!"
        )

        # Create a notification
        self.notification = Notification.objects.create(
            user=self.user2,
            message=self.message,
            content="New message from Alice"
        )

        # Create message history (simulate edit)
        self.history = MessageHistory.objects.create(
            message=self.message,
            old_content="Hi Bob",
            edited_by=self.user1
        )

    def test_delete_user_cleans_up_related_data(self):
        """
        Deleting a user should remove their messages, notifications, and histories.
        """
        response = self.client.delete(reverse("delete_user"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # User should be deleted
        self.assertFalse(User.objects.filter(username="alice").exists())

        # Messages by user1 should be deleted
        self.assertFalse(Message.objects.filter(sender=self.user1).exists())

        # Message histories by user1 should be deleted
        self.assertFalse(MessageHistory.objects.filter(edited_by=self.user1).exists())

        # Notifications tied to user1 should be deleted
        self.assertFalse(Notification.objects.filter(user=self.user1).exists())