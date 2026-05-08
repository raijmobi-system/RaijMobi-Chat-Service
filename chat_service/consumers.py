# chat_service/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.carona_id = self.scope['url_route']['kwargs']['carona_id']  # string UUID
        self.room_group_name = f'chat_{self.carona_id}'
        self.usuario_id = self.scope.get('usuario_id')  # string UUID ou None

        autorizado = await self.verificar_permissao()
        if not autorizado:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        mensagem = data.get('message')
        if not mensagem:
            return

        # Salva no banco (room já obtido pela carona_id UUID)
        room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(carona_id=self.carona_id)
        msg = await database_sync_to_async(Message.objects.create)(
            room=room, usuario_id=self.usuario_id, conteudo=mensagem
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': mensagem,
                'usuario_id': str(self.usuario_id),  # garante string
                'data_envio': msg.data_envio.isoformat(),
            }
        )

    async def chat_message(self, event):
        is_me = event['usuario_id'] == self.usuario_id
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'usuario_id': event['usuario_id'],
            'is_me': is_me,
            'data_envio': event['data_envio'],
        }))

    async def verificar_permissao(self):
        # Exemplo de chamada externa (mantida como placeholder)
        return True