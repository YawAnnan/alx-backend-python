from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer

@method_decorator(cache_page(60), name='dispatch')
class MessageListView(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer