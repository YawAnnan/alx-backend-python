from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),  # all API endpoints under /api/
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),  # include chats endpoints
]
