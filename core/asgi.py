# core/asgi.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat_service.middleware import TokenAuthMiddleware
import chat_service.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(chat_service.routing.websocket_urlpatterns)
        )
    ),
})