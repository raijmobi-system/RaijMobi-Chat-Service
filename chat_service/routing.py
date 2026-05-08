# chat_service/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # A captura agora aceita UUIDs (hex + hífens, 36 caracteres)
    re_path(r'ws/chat/(?P<carona_id>[0-9a-f-]{36})/$', consumers.ChatConsumer.as_asgi()),
]