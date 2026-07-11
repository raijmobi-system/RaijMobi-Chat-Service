# chat_service/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, UserClient

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Captura o carona_id com base na Regex do routing.py
        self.carona_id = self.scope['url_route']['kwargs']['carona_id']
        self.room_group_name = f'chat_{self.carona_id}'
        
        # Pega o ID obtido a partir da query string decodificada pelo middleware
        self.usuario_id = self.scope.get('usuario_id')

        # Permite a conexão se houver um usuário identificado
        if not self.usuario_id:
            print("❌ WebSocket rejeitado: usuario_id não encontrado no token.")
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ WebSocket conectado com sucesso! Carona: {self.carona_id} | Usuário: {self.usuario_id}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            mensagem = data.get('message')
            if not mensagem or not self.usuario_id:
                return

            # Garante que a sala exista localmente
            room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(carona_id=self.carona_id)
            
            # Garante que o UserClient exista para não violar Integridade Estrutural (FK)
            await self._ensure_user_exists(self.usuario_id)

            # Salva no banco de dados local
            msg = await database_sync_to_async(Message.objects.create)(
                room=room, usuario_id=self.usuario_id, conteudo=mensagem
            )

            # Envia o evento de volta ao grupo da sala
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': mensagem,
                    'usuario_id': str(self.usuario_id),
                    'data_envio': msg.data_envio.isoformat(),
                }
            )
        except Exception as e:
            print(f"❌ Erro ao receber/salvar mensagem no WebSocket: {e}")

    async def chat_message(self, event):
        # Envia no formato exato mapeado pelo frontend em MessageData
        is_me = event['usuario_id'] == str(self.usuario_id)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'usuario_id': event['usuario_id'],
            'is_me': is_me,
            'data_envio': event.get('data_envio')
        }))

    @database_sync_to_async
    def _ensure_user_exists(self, user_id):
        UserClient.objects.get_or_create(id=user_id, defaults={'name': 'Participante'})