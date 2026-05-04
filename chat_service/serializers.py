from rest_framework import serializers
from .models import ChatRoom, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'usuario_id', 'conteudo', 'data_envio']
        read_only_fields = ['id', 'data_envio']

class ChatRoomSerializer(serializers.ModelSerializer):
    ultima_mensagem = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'carona_id', 'ativo', 'ultima_mensagem']
        read_only_fields = ['id', 'ativo']

    def get_ultima_mensagem(self, obj):
        msg = obj.mensagens.order_by('-data_envio').first()
        if msg:
            return MessageSerializer(msg).data
        return None