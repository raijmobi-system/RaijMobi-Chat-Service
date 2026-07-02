import os
import sys
import json
import logging
import requests
from kafka import KafkaConsumer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-chat:9092')
TOPIC = 'chat_notifications'
GROUP_ID = 'chat-notification-consumer'

NOTIFICATION_API_URL = os.environ.get('NOTIFICATION_API_URL', 'http://notification-service:8000/api/notifications/')
NOTIFICATION_API_TOKEN = os.environ.get('NOTIFICATION_API_TOKEN', '')

def create_notification(user_id, message):
    headers = {'Content-Type': 'application/json'}
    if NOTIFICATION_API_TOKEN:
        headers['Authorization'] = f'Bearer {NOTIFICATION_API_TOKEN}'
    payload = {
        'user_id': user_id,
        'message': message,
        'service_origin': 'chat',
    }
    try:
        resp = requests.post(NOTIFICATION_API_URL, json=payload, headers=headers, timeout=5)
        if resp.status_code in (200, 201):
            logger.info("Notificação criada para usuário %s", user_id)
        else:
            logger.error("Erro ao criar notificação: %s - %s", resp.status_code, resp.text)
    except Exception as e:
        logger.exception("Falha ao chamar API de notificações: %s", e)

def start_consumer():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset='earliest',
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
    )
    logger.info("Consumidor de notificações iniciado. Aguardando mensagens em %s", TOPIC)
    for msg in consumer:
        data = msg.value
        user_id = data.get('user_id')
        message = data.get('message')
        if user_id and message:
            create_notification(user_id, message)
        else:
            logger.warning("Mensagem inválida: %s", data)

if __name__ == '__main__':
    start_consumer()