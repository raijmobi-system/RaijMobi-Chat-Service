# chat_service/serializers.py
from rest_framework import serializers
from .models import UserClient, ChatRoom, Message

class UserClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserClient
        fields = ['id', 'name', 'is_rider', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class MessageSerializer(serializers.ModelSerializer):
    usuario_id = serializers.UUIDField(write_only=True)   # recebe UUID externo
    usuario_nome = serializers.CharField(source='usuario.name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'usuario_id', 'usuario_nome', 'conteudo', 'data_envio']
        read_only_fields = ['id', 'data_envio', 'room', 'usuario_nome']

    def validate_usuario_id(self, value):
        """Verifica se o usuário existe no banco local"""
        if not UserClient.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Usuário com id {value} não encontrado.")
        return value

class ChatRoomSerializer(serializers.ModelSerializer):
    created_by_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'carona_id', 'ativo', 'criado_em', 'created_by_id', 'created_by_name']
        read_only_fields = ['id', 'criado_em', 'created_by_name']

    def validate_created_by_id(self, value):
        if value is not None and not UserClient.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Usuário com id {value} não encontrado.")
        return value