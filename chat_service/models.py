# chat_service/models.py
import uuid
from django.db import models

class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ID da carona agora é UUID (recebido do serviço externo)
    carona_id = models.UUIDField(unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Room carona {self.carona_id}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='mensagens')
    # ID do usuário agora é UUID (recebido do serviço externo)
    usuario_id = models.UUIDField()
    conteudo = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_envio']

    def __str__(self):
        return f"{self.usuario_id} em {self.room.carona_id}: {self.conteudo[:30]}"