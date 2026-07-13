# import json
# import logging
# from kafka import KafkaProducer, KafkaAdminClient
# from kafka.admin import NewTopic
# from kafka.errors import TopicAlreadyExistsError
# from django.conf import settings

# logger = logging.getLogger(__name__)
# producer = None

# def get_producer():
#     global producer
#     if producer is None:
#         try:
#             producer = KafkaProducer(
#                 bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
#                 value_serializer=lambda v: json.dumps(v).encode('utf-8'),
#                 key_serializer=lambda k: k.encode('utf-8') if k else None,
#             )
#         except Exception as e:
#             logger.error("Falha ao criar produtor Kafka: %s", e)
#     return producer

# def send_chat_notification(user_id, message):
#     prod = get_producer()
#     if prod is None:
#         logger.warning("Produtor não disponível, notificação não enviada.")
#         return

#     # Garante que o tópico chat_notifications exista
#     try:
#         admin = KafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
#         topic_list = [NewTopic(name='chat_notifications', num_partitions=1, replication_factor=1)]
#         admin.create_topics(new_topics=topic_list, validate_only=False)
#     except TopicAlreadyExistsError:
#         pass
#     except Exception as e:
#         logger.error("Erro ao criar tópico chat_notifications: %s", e)
#     finally:
#         try:
#             admin.close()
#         except:
#             pass

#     data = {
#         'user_id': str(user_id),
#         'message': message,
#     }
#     try:
#         future = prod.send('chat_notifications', key=str(user_id), value=data)
#         future.get(timeout=5)
#         logger.info("Notificação de chat enviada para %s", user_id)
#     except Exception as e:
#         logger.error("Falha ao enviar notificação de chat: %s", e)

import sys
import os

# Adiciona o diretório raiz ao path (antes do Django setup)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from kafka import KafkaProducer, KafkaAdminClient, KafkaConsumer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from django.conf import settings
import django

# Configura o Django para acessar os modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chat_service.models import UserClient

logger = logging.getLogger(__name__)
producer = None

# ============================================================
# PRODUTOR DE NOTIFICAÇÕES (usado pelas views)
# ============================================================
def get_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
            )
        except Exception as e:
            logger.error("Falha ao criar produtor Kafka: %s", e)
    return producer

def send_chat_notification(user_id, message):
    prod = get_producer()
    if prod is None:
        logger.warning("Produtor não disponível, notificação não enviada.")
        return

    # Garante que o tópico chat_notifications exista
    try:
        admin = KafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        topic_list = [NewTopic(name='chat_notifications', num_partitions=1, replication_factor=1)]
        admin.create_topics(new_topics=topic_list, validate_only=False)
    except TopicAlreadyExistsError:
        pass
    except Exception as e:
        logger.error("Erro ao criar tópico chat_notifications: %s", e)
    finally:
        try:
            admin.close()
        except:
            pass

    data = {'user_id': str(user_id), 'message': message}
    try:
        future = prod.send('chat_notifications', key=str(user_id), value=data)
        future.get(timeout=5)
        logger.info("Notificação de chat enviada para %s", user_id)
    except Exception as e:
        logger.error("Falha ao enviar notificação de chat: %s", e)


# ============================================================
# CONSUMIDOR DE USUÁRIOS (executado quando o script é chamado)
# ============================================================
def start_user_consumer():
    KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-user:9092')
    TOPIC = 'user-events'
    GROUP_ID = 'chat-service-user-consumer'

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset='earliest',
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
    )

    logger.info("🔄 Consumidor de usuários iniciado. Aguardando mensagens no tópico %s", TOPIC)

    for message in consumer:
        try:
            user_data = message.value
            user_id = user_data.get('id')
            name = user_data.get('name', 'Usuário')
            is_rider = user_data.get('is_rider', False)

            if not user_id:
                logger.warning("Mensagem sem 'id' ignorada: %s", user_data)
                continue

            obj, created = UserClient.objects.update_or_create(
                id=user_id,
                defaults={'name': name, 'is_rider': is_rider}
            )
            status = 'criado' if created else 'atualizado'
            logger.info("👤 Usuário %s (%s) %s com sucesso.", user_id, name, status)

        except Exception as e:
            logger.exception("Erro ao processar mensagem de usuário: %s", e)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    start_user_consumer()