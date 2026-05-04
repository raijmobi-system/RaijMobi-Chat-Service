import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.carona_id = self.scope['url_route']['kwargs']['carona_id']
        self.room_group_name = f'chat_{self.carona_id}'
        self.usuario_id = self.scope.get('usuario_id')  # injetado via middleware customizado (ver abaixo)

        # Verificar se o usuário pode acessar essa sala (chamada REST ao serviço de caronas)
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

        # Salva no banco
        room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(carona_id=self.carona_id)
        msg = await database_sync_to_async(Message.objects.create)(
            room=room, usuario_id=self.usuario_id, conteudo=mensagem
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': mensagem,
                'usuario_id': self.usuario_id,
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
        # Chamada HTTP ao serviço de caronas para saber se usuário pode participar
        # Exemplo com httpx assíncrono
        return True
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     resp = await client.get(
        #         f"http://carona-service/api/caronas/{self.carona_id}/autorizado/",
        #         params={'usuario_id': self.usuario_id}
        #     )
        #     return resp.status_code == 200 and resp.json().get('autorizado', False)