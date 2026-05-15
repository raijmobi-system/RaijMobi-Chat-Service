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
    # authentication_classes = [ServiceTokenAuthentication]
    # permission_classes = [IsServiceAuthenticated]

    def get_queryset(self):
        carona_id = self.kwargs['carona_id']  # string UUID
        return Message.objects.filter(room__carona_id=carona_id)

    def perform_create(self, serializer):
        carona_id = self.kwargs['carona_id']
        room, _ = ChatRoom.objects.get_or_create(carona_id=carona_id)
        serializer.save(room=room, usuario_id=self.request.data.get('usuario_id'))


class RoomListCreate(generics.ListCreateAPIView):
    """
    GET  /api/chat/rooms/ → listar todas as salas (opcional)
    POST /api/chat/rooms/ → criar uma nova sala com carona_id
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    # authentication_classes = [ServiceTokenAuthentication]
    # permission_classes = [IsServiceAuthenticated]

    def post(self, request, *args, **kwargs):
        carona_id = request.data.get('carona_id')
        if not carona_id:
            return Response({'error': 'campo carona_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se já existe uma sala para essa carona
        room, created = ChatRoom.objects.get_or_create(carona_id=carona_id)
        if created:
            serializer = self.get_serializer(room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'sala já existe'}, status=status.HTTP_409_CONFLICT)
