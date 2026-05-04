from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware(BaseMiddleware):
    """
    Middleware customizado para autenticação de WebSocket via token.
    Extrai o token da query string (?token=...) e um usuario_id opcional.
    """
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = dict(
            qc.split("=") for qc in query_string.split("&") if "=" in qc
        )
        token = params.get("token", "")

        if token == settings.SERVICE_API_KEY:
            # Token de serviço válido
            usuario_id = params.get("usuario_id")
            scope["usuario_id"] = int(usuario_id) if usuario_id else None
        else:
            scope["usuario_id"] = None

        scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)