# chat_service/middleware.py
import jwt
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        
        # Faz o parse dos parâmetros da URL
        params = dict(
            qc.split("=") for qc in query_string.split("&") if "=" in qc
        )
        
        token = params.get("token", None)
        usuario_id = None
        
        if token:
            try:
                # Abre o JWT enviado pelo frontend Next.js para coletar o user_id
                payload = jwt.decode(token, options={"verify_signature": False})
                usuario_id = payload.get("user_id")
            except Exception as e:
                print(f"⚠️ Erro ao decodificar JWT no Middleware: {e}")

        # Injeta nos escopos que os consumers usam
        scope["usuario_id"] = usuario_id
        scope["user_id"] = usuario_id
        scope["user"] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)