# # chat_service/models.py
# import uuid
# from django.db import models

# class ChatRoom(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     # ID da carona agora é UUID (recebido do serviço externo)
#     carona_id = models.UUIDField(unique=True)
#     criado_em = models.DateTimeField(auto_now_add=True)
#     ativo = models.BooleanField(default=True)

#     def __str__(self):
#         return f"Room carona {self.carona_id}"


# class Message(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='mensagens')
#     # ID do usuário agora é UUID (recebido do serviço externo)
#     usuario_id = models.UUIDField()
#     conteudo = models.TextField()
#     data_envio = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['data_envio']

#     def __str__(self):
#         return f"{self.usuario_id} em {self.room.carona_id}: {self.conteudo[:30]}"

# # chat_service/models.py
# from django.db import models
# from easyaudit.models import CRUDEvent
# from django.contrib.contenttypes.models import ContentType

# class ChatRoomAudit(CRUDEvent):
#     class Meta:
#         proxy = True
#         verbose_name = 'Auditoria ChatRoom'
#         verbose_name_plural = 'Auditoria ChatRooms'

# class MessageAudit(CRUDEvent):
#     class Meta:
#         proxy = True
#         verbose_name = 'Auditoria Mensagem'
#         verbose_name_plural = 'Auditoria Mensagens'

# chat_service/models.py
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from easyaudit.models import CRUDEvent

# ==========================================
# MODELO USUÁRIO (igual ao ride_service)
# ==========================================
class UserClient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    is_rider = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ==========================================
# SALA DE CHAT (AGORA COM created_by)
# ==========================================
class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    carona_id = models.UUIDField(unique=True)          # ID da carona (serviço externo)
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        UserClient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salas_criadas',
        help_text="Usuário que criou a sala (opcional)"
    )

    def __str__(self):
        return f"Room carona {self.carona_id}"


# ==========================================
# MENSAGEM (referencia UserClient via FK)
# ==========================================
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='mensagens')
    usuario = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='mensagens')
    conteudo = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_envio']

    def __str__(self):
        return f"{self.usuario.name} em {self.room.carona_id}: {self.conteudo[:30]}"


# ==========================================
# PROXIES PARA AUDITORIA (easyaudit)
# ==========================================
class ChatRoomAudit(CRUDEvent):
    class Meta:
        proxy = True
        verbose_name = 'Auditoria ChatRoom'
        verbose_name_plural = 'Auditoria ChatRooms'

class MessageAudit(CRUDEvent):
    class Meta:
        proxy = True
        verbose_name = 'Auditoria Mensagem'
        verbose_name_plural = 'Auditoria Mensagens'