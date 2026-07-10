# chat_service/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import UserClient, ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from .notification_producer import send_chat_notification
from django.db import transaction
from .metrics import chat_rooms_total, messages_total
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from easyaudit.models import CRUDEvent
from django.db.models import Q

class AdminLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        busca = request.query_params.get('busca', '')
        
        # ♻️ Fatiamento [:100] removido para carregar todos os logs existentes
        queryset = CRUDEvent.objects.select_related('user', 'content_type').all().order_by('-datetime')

        if busca:
            queryset = queryset.filter(
                Q(user__username__icontains=busca) | 
                Q(object_repr__icontains=busca) | 
                Q(content_type__model__icontains=busca)
            )

        dados = []
        for log in queryset:
            dados.append({
                "id": str(log.id),
                "user_name": log.user.username if log.user else "Sistema",
                "content_type": log.content_type.name if log.content_type else "Modelo Oculto",
                "object_repr": log.object_repr,
                "event_type": log.event_type, # 1=Criar, 2=Editar, 3=Deletar nativos do Easy Audit
                "datetime": log.datetime.isoformat()
            })

        return Response(dados)

class RoomDetail(generics.RetrieveAPIView):
    """GET /api/rooms/{carona_id}/"""
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    lookup_field = 'carona_id'

class MessageList(generics.ListCreateAPIView):
    """GET /api/rooms/{carona_id}/messages/  |  POST /api/rooms/{carona_id}/messages/"""
    serializer_class = MessageSerializer

    def get_queryset(self):
        carona_id = self.kwargs['carona_id']
        return Message.objects.filter(room__carona_id=carona_id)

    def perform_create(self, serializer):
        carona_id = self.kwargs['carona_id']
        room, _ = ChatRoom.objects.get_or_create(carona_id=carona_id)
        usuario = UserClient.objects.get(id=serializer.validated_data['usuario_id'])
        message = serializer.save(room=room, usuario=usuario)
        messages_total.inc()

        logger.info("Mensagem salva, room: %s, sender: %s", room.carona_id, usuario.id)
        transaction.on_commit(lambda: self._send_chat_notifications(room, usuario, message))

    def _send_chat_notifications(self, room, sender, message):
        logger.info("Enviando notificações para sala %s", room.carona_id)
        participants = set()
        if room.driver:
            participants.add(room.driver.id)
            logger.info("Driver: %s", room.driver.id)
        passengers = list(room.passengers.values_list('id', flat=True))
        logger.info("Passageiros: %s", passengers)
        participants.update(passengers)
        participants.discard(sender.id)
        logger.info("Participantes finais para notificar: %s", participants)

        for user_id in participants:
            msg_text = f"Nova mensagem de {sender.name} no chat da carona {room.carona_id}"
            logger.info("Chamando send_chat_notification para %s", user_id)
            send_chat_notification(user_id, msg_text)

class RoomListCreate(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        # 1. Pegamos os cabeçalhos reais que estão vindo na requisição
        user_id = self.request.META.get('HTTP_X_USER_ID')
        all_headers = self.request.META
        
        # 2. Vamos printar no console do chat-service para auditar o que está vindo
        print("🔍 [DEBUG CHAT] ID do Usuário capturado no Header:", user_id)
        # Se quiser ver se o Kong está usando outro nome, descomente a linha abaixo:
        # print("📋 [DEBUG HEADERS] Todos os metadados da requisição:", all_headers)

        # 3. TESTE DESBLOQUEIO: Se o user_id for nulo, vamos forçar o retorno de TUDO
        if not user_id:
            print("⚠️ Cabeçalho X-User-Id não encontrado! Retornando todas as salas para teste.")
            return ChatRoom.objects.all() 
            
        # Filtro original baseado no ID
        return ChatRoom.objects.filter(
            Q(driver__id=user_id) | Q(passengers__id=user_id)
        ).distinct()

    def post(self, request, *args, **kwargs):
        carona_id = request.data.get('carona_id')
        driver_id = request.data.get('driver_id')
        passenger_ids = request.data.get('passenger_ids', [])

        if isinstance(passenger_ids, str):
            passenger_ids = [passenger_ids]

        if not carona_id:
            return Response(
                {'error': 'campo carona_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if ChatRoom.objects.filter(carona_id=carona_id).exists():
            return Response(
                {'error': 'sala já existe'},
                status=status.HTTP_409_CONFLICT
            )

        driver = None
        if driver_id:
            driver, _ = UserClient.objects.get_or_create(
                id=driver_id,
                defaults={'name': f'Motorista {driver_id[:8]}', 'is_rider': False}
            )

        room = ChatRoom.objects.create(carona_id=carona_id, driver=driver)
        chat_rooms_total.inc()

        for pid in passenger_ids:
            passenger, _ = UserClient.objects.get_or_create(
                id=pid,
                defaults={'name': f'Passageiro {pid[:8]}', 'is_rider': True}
            )
            room.passengers.add(passenger)

        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)