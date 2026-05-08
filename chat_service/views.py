from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from .authentication import ServiceTokenAuthentication  # autenticação customizada
from rest_framework import permissions

class IsServiceAuthenticated(permissions.BasePermission):
    """
    Permite acesso se a autenticação via ServiceTokenAuthentication foi bem‑sucedida
    (request.auth contém o token válido).
    """
    def has_permission(self, request, view):
        return request.auth is not None

class RoomDetail(generics.RetrieveAPIView):
    """
    GET /api/rooms/{carona_id}/ → dados da sala
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    lookup_field = 'carona_id' 

class MessageList(generics.ListCreateAPIView):
    """
    GET  /api/rooms/{carona_id}/messages/ → histórico
    POST /api/rooms/{carona_id}/messages/ → enviar mensagem (via REST)
    """
    serializer_class = MessageSerializer
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsServiceAuthenticated]

    def get_queryset(self):
        carona_id = self.kwargs['carona_id']  # string UUID
        return Message.objects.filter(room__carona_id=carona_id)

    def perform_create(self, serializer):
        carona_id = self.kwargs['carona_id']
        room, _ = ChatRoom.objects.get_or_create(carona_id=carona_id)
        serializer.save(room=room, usuario_id=self.request.data.get('usuario_id'))