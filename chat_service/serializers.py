from rest_framework import serializers
from .models import ChatRoom, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'usuario_id', 'conteudo', 'data_envio']
        read_only_fields = ['id', 'data_envio']

class ChatRoomSerializer(serializers.ModelSerializer):
    # ultima_mensagem foi removido
    class Meta:
        model = ChatRoom
        fields = ['id', 'carona_id', 'ativo']   # sem ultima_mensagem
        read_only_fields = ['id', 'ativo']
