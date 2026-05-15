# chat_service/middleware.py
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = dict(
            qc.split("=") for qc in query_string.split("&") if "=" in qc
        )
        # Apenas pega o usuario_id, sem verificar token
        usuario_id = params.get("usuario_id", None)
        scope["usuario_id"] = usuario_id
        scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)
