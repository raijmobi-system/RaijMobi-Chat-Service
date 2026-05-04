from rest_framework import authentication, exceptions
from django.conf import settings

class ServiceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token != settings.SERVICE_API_KEY:
            raise exceptions.AuthenticationFailed('Token de serviço inválido')
        return (None, token)   # usuário anônimo, mas autorizado como serviço