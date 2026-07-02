# chat_service/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import UserClient, ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from .notification_producer import send_chat_notification
from django.db import transaction
from .metrics import chat_rooms_total,messages_total
import logging
logger = logging.getLogger(__name__)

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
        # Obtém ou cria a sala (sem created_by ainda)
        room, _ = ChatRoom.objects.get_or_create(carona_id=carona_id)

        # Pega o usuario_id enviado na requisição (campo write_only)
        usuario_id = serializer.validated_data.get('usuario_id')
        usuario = UserClient.objects.get(id=usuario_id)  # já validado no serializer

        serializer.save(room=room, usuario=usuario)

    # def perform_create(self, serializer):
    #     carona_id = self.kwargs['carona_id']
    #     room, _ = ChatRoom.objects.get_or_create(carona_id=carona_id)
    #     usuario = UserClient.objects.get(id=serializer.validated_data['usuario_id'])
    #     message = serializer.save(room=room, usuario=usuario)

    #     messages_total.inc()

    #     # Envia notificações para os outros participantes após o commit
    #     transaction.on_commit(lambda: self._send_chat_notifications(room, usuario, message))

    # def _send_chat_notifications(self, room, sender, message):
    #     # Lista de IDs dos participantes (motorista + passageiros)
    #     participants = set()
    #     if room.driver:
    #         participants.add(room.driver.id)
    #     participants.update(room.passengers.values_list('id', flat=True))
    #     participants.discard(sender.id)  # remove o remetente

    #     for user_id in participants:
    #         msg_text = f"Nova mensagem de {sender.name} no chat da carona {room.carona_id}"
    #         send_chat_notification(user_id, msg_text)


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

# class RoomListCreate(generics.ListCreateAPIView):
#     queryset = ChatRoom.objects.all()
#     serializer_class = ChatRoomSerializer

#     def post(self, request, *args, **kwargs):
#         carona_id = request.data.get('carona_id')
#         driver_id = request.data.get('driver_id')
#         passenger_ids = request.data.get('passenger_ids', [])  # lista de UUIDs

#         if isinstance(passenger_ids, str):
#             passenger_ids = [passenger_ids] 

#         if not carona_id:
#             return Response({'error': 'campo carona_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

#         if ChatRoom.objects.filter(carona_id=carona_id).exists():
#             return Response({'error': 'sala já existe'}, status=status.HTTP_409_CONFLICT)

#         driver = None
#         if driver_id:
#             try:
#                 driver = UserClient.objects.get(id=driver_id)
#             except UserClient.DoesNotExist:
#                 return Response({'error': f'Motorista com id {driver_id} não encontrado'},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         room = ChatRoom.objects.create(carona_id=carona_id, driver=driver)

#         chat_rooms_total.inc()

#         # Adiciona os passageiros
#         for pid in passenger_ids:
#             try:
#                 passenger = UserClient.objects.get(id=pid)
#                 room.passengers.add(passenger)
#             except UserClient.DoesNotExist:
#                 # Opcional: logar ou ignorar
#                 pass

#         serializer = self.get_serializer(room)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)



class RoomListCreate(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

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

        # Garante que o motorista exista (cria se necessário)
        driver = None
        if driver_id:
            driver, _ = UserClient.objects.get_or_create(
                id=driver_id,
                defaults={'name': f'Motorista {driver_id[:8]}', 'is_rider': False}
            )

        room = ChatRoom.objects.create(carona_id=carona_id, driver=driver)
        chat_rooms_total.inc()

        # Garante que os passageiros existam
        for pid in passenger_ids:
            passenger, _ = UserClient.objects.get_or_create(
                id=pid,
                defaults={'name': f'Passageiro {pid[:8]}', 'is_rider': True}
            )
            room.passengers.add(passenger)

        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)