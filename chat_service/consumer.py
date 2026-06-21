import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from kafka import KafkaConsumer
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chat_service.models import UserClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-user:9092')
TOPIC = 'user-events'

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id='chat-service',
    auto_offset_reset='earliest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
)

logger.info("Consumer iniciado, aguardando mensagens no tópico %s", TOPIC)

try:
    for message in consumer:
        try:
            user_data = message.value
            user_id = user_data['id']
            name = user_data['name']
            is_rider = user_data.get('is_rider', False)

            obj, created = UserClient.objects.update_or_create(
                id=user_id,
                defaults={'name': name, 'is_rider': is_rider}
            )
            status = 'criado' if created else 'atualizado'
            logger.info("Usuário %s (%s) %s com sucesso.", user_id, name, status)
        except Exception as e:
            logger.exception("Erro ao processar mensagem: %s", e)
except KeyboardInterrupt:
    logger.info("Consumer encerrado.")