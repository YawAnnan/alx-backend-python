from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils import timezone

from .models import Message


@cache_page(60)
def message_list(request, conversation_id):
    """
    Displays all messages in a conversation with caching (60s)
    and ORM optimization using .only().
    """
    messages = Message.objects.filter(conversation_id=conversation_id).only(
        "id", "sender", "receiver", "content", "timestamp"
    )

    return render(request, "messaging/message_list.html", {"messages": messages})