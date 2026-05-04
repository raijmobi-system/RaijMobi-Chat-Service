# # """
# # ASGI config for core project.

# # It exposes the ASGI callable as a module-level variable named ``application``.

# # For more information on this file, see
# # https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
# # """

# # # import os

# # # from django.core.asgi import get_asgi_application

# # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# # # application = get_asgi_application()


# # # import os
# # # from django.core.asgi import get_asgi_application
# # # from channels.routing import ProtocolTypeRouter, URLRouter
# # # from channels.auth import AuthMiddlewareStack
# # # from chat_service.middleware import TokenAuthMiddleware  # ajuste conforme seu projeto
# # # import chat_service.routing

# # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# # # application = ProtocolTypeRouter({
# # #     "http": get_asgi_application(),
# # #     "websocket": TokenAuthMiddleware(
# # #         AuthMiddlewareStack(
# # #             URLRouter(chat_service.routing.websocket_urlpatterns)
# # #         )
# # #     ),
# # # })


# # # import os
# # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # ← primeiro!

# # # from django.core.asgi import get_asgi_application
# # # from channels.routing import ProtocolTypeRouter, URLRouter
# # # from channels.auth import AuthMiddlewareStack
# # # from chat_service.middleware import TokenAuthMiddleware
# # # import chat_service.routing

# # # application = ProtocolTypeRouter({
# # #     "http": get_asgi_application(),
# # #     "websocket": TokenAuthMiddleware(
# # #         AuthMiddlewareStack(
# # #             URLRouter(chat_service.routing.websocket_urlpatterns)
# # #         )
# # #     ),
# # # })


# # import os
# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# # import django
# # django.setup()                       # <-- garante que o app registry está pronto

# # from django.core.asgi import get_asgi_application
# # from channels.routing import ProtocolTypeRouter, URLRouter
# # from channels.auth import AuthMiddlewareStack
# # from chat_service.middleware import TokenAuthMiddleware
# # import chat_service.routing

# # application = ProtocolTypeRouter({
# #     "http": get_asgi_application(),
# #     "websocket": TokenAuthMiddleware(
# #         AuthMiddlewareStack(
# #             URLRouter(chat_service.routing.websocket_urlpatterns)
# #         )
# #     ),
# # })



# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from chat_service.middleware import TokenAuthMiddleware
# import chat_service.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": TokenAuthMiddleware(
#         AuthMiddlewareStack(
#             URLRouter(chat_service.routing.websocket_urlpatterns)
#         )
#     ),
# })


import os
import django

# 1. Define o módulo de configurações
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. Inicializa o Django explicitamente AGORA (antes de importar o middleware)
django.setup()

# 3. Agora é seguro importar o que depende de modelos e o ASGI
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