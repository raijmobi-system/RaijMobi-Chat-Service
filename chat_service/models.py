# Create your models here.
from django.db import models

class ChatRoom(models.Model):
    """
    Representa uma sala de chat vinculada a uma carona (por ID).
    """
    carona_id = models.PositiveIntegerField(unique=True)   # ID da carona no serviço de caronas
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)             # false se carona foi finalizada

    def __str__(self):
        return f"Room carona {self.carona_id}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='mensagens')
    usuario_id = models.PositiveIntegerField()            # ID do usuário no serviço de usuários
    conteudo = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_envio']

    def __str__(self):
        return f"{self.usuario_id} em {self.room.carona_id}: {self.conteudo[:30]}"