# # # import json
# # # import logging
# # # from kafka import KafkaProducer
# # # from django.conf import settings

# # # logger = logging.getLogger(__name__)
# # # producer = None

# # # def get_producer():
# # #     global producer
# # #     if producer is None:
# # #         try:
# # #             producer = KafkaProducer(
# # #                 bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,  # mesmo broker do user
# # #                 value_serializer=lambda v: json.dumps(v).encode('utf-8'),
# # #                 key_serializer=lambda k: k.encode('utf-8') if k else None,
# # #             )
# # #         except Exception as e:
# # #             logger.error("Falha ao criar produtor Kafka: %s", e)
# # #     return producer

# # # def send_chat_notification(user_id, message):
# # #     prod = get_producer()
# # #     if prod is None:
# # #         logger.warning("Produtor não disponível, notificação não enviada.")
# # #         return
# # #     data = {
# # #         'user_id': str(user_id),
# # #         'message': message,
# # #     }
# # #     try:
# # #         future = prod.send('chat_notifications', key=str(user_id), value=data)  # ← AQUI
# # #         future.get(timeout=5)
# # #         logger.info("Notificação de chat enviada para %s", user_id)
# # #     except Exception as e:
# # #         logger.error("Falha ao enviar notificação de chat: %s", e)


# # import json
# # import logging
# # from kafka import KafkaProducer, KafkaAdminClient
# # from kafka.admin import NewTopic
# # from kafka.errors import TopicAlreadyExistsError, KafkaError
# # from django.conf import settings

# # logger = logging.getLogger(__name__)
# # producer = None

# # def get_producer():
# #     global producer
# #     if producer is None:
# #         try:
# #             logger.info("Criando produtor Kafka com bootstrap: %s", settings.KAFKA_BOOTSTRAP_SERVERS)
# #             producer = KafkaProducer(
# #                 bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
# #                 value_serializer=lambda v: json.dumps(v).encode('utf-8'),
# #                 key_serializer=lambda k: k.encode('utf-8') if k else None,
# #             )
# #             logger.info("Produtor criado com sucesso.")
# #         except Exception as e:
# #             logger.error("Falha ao criar produtor Kafka: %s", e, exc_info=True)
# #     return producer

# # def send_chat_notification(user_id, message):
# #     prod = get_producer()
# #     if prod is None:
# #         logger.warning("Produtor não disponível, notificação não enviada.")
# #         return

# #     # Garante que o tópico chat_notifications exista
# #     try:
# #         admin = KafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
# #         topic_list = [NewTopic(name='chat_notifications', num_partitions=1, replication_factor=1)]
# #         admin.create_topics(new_topics=topic_list, validate_only=False)
# #         logger.info("Tópico chat_notifications verificado/criado.")
# #     except TopicAlreadyExistsError:
# #         logger.debug("Tópico chat_notifications já existe.")
# #     except Exception as e:
# #         logger.error("Erro ao criar tópico chat_notifications: %s", e, exc_info=True)
# #     finally:
# #         try:
# #             admin.close()
# #         except:
# #             pass

# #     data = {
# #         'user_id': str(user_id),
# #         'message': message,
# #     }
# #     try:
# #         logger.info("Enviando mensagem para tópico chat_notifications: %s", data)
# #         future = prod.send('chat_notifications', key=str(user_id), value=data)
# #         future.get(timeout=5)
# #         logger.info("Notificação de chat enviada para %s", user_id)
# #     except Exception as e:
# #         logger.error("Falha ao enviar notificação de chat: %s", e, exc_info=True)


# # chat_service/notification_consumer.py
# import os
# import sys
# import json
# import logging
# import requests
# from kafka import KafkaConsumer

# # Configura Django
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# import django
# django.setup()

# from django.conf import settings

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# KAFKA_BOOTSTRAP = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-chat:9092')
# TOPIC = 'chat_notifications'
# GROUP_ID = 'chat-notification-consumer'

# # URL do serviço de notificações (ajuste para o endereço correto)
# NOTIFICATION_API_URL = os.environ.get('NOTIFICATION_API_URL', 'http://notification-service:8000/api/notifications/')
# # Se o serviço de notificações espera um token, coloque aqui
# NOTIFICATION_API_TOKEN = os.environ.get('NOTIFICATION_API_TOKEN', '')

# def create_notification(user_id, message):
#     """Chama a API do serviço de notificações para criar uma notificação."""
#     headers = {'Content-Type': 'application/json'}
#     if NOTIFICATION_API_TOKEN:
#         headers['Authorization'] = f'Bearer {NOTIFICATION_API_TOKEN}'

#     payload = {
#         'user_id': user_id,
#         'message': message,
#         'service_origin': 'chat',  # ou o campo que o serviço espera
#     }
#     try:
#         resp = requests.post(NOTIFICATION_API_URL, json=payload, headers=headers, timeout=5)
#         if resp.status_code in (200, 201):
#             logger.info("Notificação criada para usuário %s", user_id)
#         else:
#             logger.error("Erro ao criar notificação: %s - %s", resp.status_code, resp.text)
#     except Exception as e:
#         logger.exception("Falha ao chamar API de notificações: %s", e)

# def start_consumer():
#     consumer = KafkaConsumer(
#         TOPIC,
#         bootstrap_servers=KAFKA_BOOTSTRAP,
#         group_id=GROUP_ID,
#         auto_offset_reset='earliest',
#         value_deserializer=lambda v: json.loads(v.decode('utf-8')),
#         key_deserializer=lambda k: k.decode('utf-8') if k else None,
#     )
#     logger.info("Consumidor de notificações iniciado. Aguardando mensagens em %s", TOPIC)

#     for msg in consumer:
#         data = msg.value
#         user_id = data.get('user_id')
#         message = data.get('message')
#         if user_id and message:
#             create_notification(user_id, message)
#         else:
#             logger.warning("Mensagem inválida: %s", data)

# if __name__ == '__main__':
#     start_consumer()



import json
import logging
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from django.conf import settings

logger = logging.getLogger(__name__)
producer = None

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

    # Garante que o tópico exista
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