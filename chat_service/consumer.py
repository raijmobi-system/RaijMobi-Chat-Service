# # # # # # import sys
# # # # # # import os

# # # # # # # Adiciona o diretório raiz do projeto ao path
# # # # # # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # # # # # import json
# # # # # # import logging
# # # # # # from kafka import KafkaConsumer
# # # # # # import django

# # # # # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# # # # # # django.setup()

# # # # # # from chat_service.models import UserClient

# # # # # # logging.basicConfig(level=logging.INFO)
# # # # # # logger = logging.getLogger(__name__)

# # # # # # KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-user:9092')
# # # # # # TOPIC = 'user-events'

# # # # # # consumer = KafkaConsumer(
# # # # # #     TOPIC,
# # # # # #     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
# # # # # #     group_id='chat-service',
# # # # # #     auto_offset_reset='earliest',
# # # # # #     value_deserializer=lambda v: json.loads(v.decode('utf-8')),
# # # # # #     key_deserializer=lambda k: k.decode('utf-8') if k else None,
# # # # # # )

# # # # # # logger.info("Consumer iniciado, aguardando mensagens no tópico %s", TOPIC)

# # # # # # try:
# # # # # #     for message in consumer:
# # # # # #         try:
# # # # # #             user_data = message.value
# # # # # #             user_id = user_data['id']
# # # # # #             name = user_data['name']
# # # # # #             is_rider = user_data.get('is_rider', False)

# # # # # #             obj, created = UserClient.objects.update_or_create(
# # # # # #                 id=user_id,
# # # # # #                 defaults={'name': name, 'is_rider': is_rider}
# # # # # #             )
# # # # # #             status = 'criado' if created else 'atualizado'
# # # # # #             logger.info("Usuário %s (%s) %s com sucesso.", user_id, name, status)
# # # # # #         except Exception as e:
# # # # # #             logger.exception("Erro ao processar mensagem: %s", e)
# # # # # # except KeyboardInterrupt:
# # # # # #     logger.info("Consumer encerrado.")


# # # # # import sys
# # # # # import os

# # # # # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # # # # import json
# # # # # import logging
# # # # # from kafka import KafkaConsumer, KafkaAdminClient
# # # # # from kafka.admin import NewTopic
# # # # # from kafka.errors import KafkaError
# # # # # import django

# # # # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# # # # # django.setup()

# # # # # from chat_service.models import UserClient

# # # # # logging.basicConfig(level=logging.INFO)
# # # # # logger = logging.getLogger(__name__)

# # # # # KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-user:9092')
# # # # # TOPIC = 'user-events'
# # # # # GROUP_ID = 'chat-service'  # pode ser fixo agora

# # # # # def reset_offsets_if_empty():
# # # # #     """Reseta os offsets do grupo se a tabela de usuários estiver vazia."""
# # # # #     if UserClient.objects.count() == 0:
# # # # #         logger.info("Banco de usuários vazio. Resetando offsets do grupo %s para earliest.", GROUP_ID)
# # # # #         try:
# # # # #             admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
# # # # #             # Obtém partições do tópico
# # # # #             topic_partitions = admin.describe_topics([TOPIC])[0]['partitions']
# # # # #             partitions = [f"{TOPIC}-{p['partition']}" for p in topic_partitions]
# # # # #             # Reseta offsets
# # # # #             admin.alter_consumer_group_offsets(
# # # # #                 group_id=GROUP_ID,
# # # # #                 offsets={tp: 0 for tp in partitions}
# # # # #             )
# # # # #             logger.info("Offsets resetados com sucesso.")
# # # # #         except Exception as e:
# # # # #             logger.error("Falha ao resetar offsets: %s", e)
# # # # #         finally:
# # # # #             admin.close()

# # # # # # Executa reset antes de criar o consumer
# # # # # reset_offsets_if_empty()

# # # # # consumer = KafkaConsumer(
# # # # #     TOPIC,
# # # # #     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
# # # # #     group_id=GROUP_ID,
# # # # #     auto_offset_reset='earliest',
# # # # #     value_deserializer=lambda v: json.loads(v.decode('utf-8')),
# # # # #     key_deserializer=lambda k: k.decode('utf-8') if k else None,
# # # # # )

# # # # # logger.info("Consumer iniciado, aguardando mensagens no tópico %s", TOPIC)

# # # # # try:
# # # # #     for message in consumer:
# # # # #         try:
# # # # #             user_data = message.value
# # # # #             user_id = user_data['id']
# # # # #             name = user_data['name']
# # # # #             is_rider = user_data.get('is_rider', False)

# # # # #             obj, created = UserClient.objects.update_or_create(
# # # # #                 id=user_id,
# # # # #                 defaults={'name': name, 'is_rider': is_rider}
# # # # #             )
# # # # #             status = 'criado' if created else 'atualizado'
# # # # #             logger.info("Usuário %s (%s) %s com sucesso.", user_id, name, status)
# # # # #         except Exception as e:
# # # # #             logger.exception("Erro ao processar mensagem: %s", e)
# # # # # except KeyboardInterrupt:
# # # # #     logger.info("Consumer encerrado.")


# # # # import sys
# # # # import os

# # # # # Adiciona o diretório raiz do projeto ao path
# # # # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # # # import json
# # # # import logging
# # # # from kafka import KafkaConsumer, KafkaAdminClient
# # # # from kafka.errors import KafkaError
# # # # import django

# # # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# # # # django.setup()

# # # # from chat_service.models import UserClient

# # # # logging.basicConfig(level=logging.INFO)
# # # # logger = logging.getLogger(__name__)

# # # # KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-user:9092')
# # # # TOPIC = 'user-events'
# # # # GROUP_ID = 'chat-service'               # fixo, não precisa mudar


# # # # def reset_offsets_if_empty():
# # # #     """Se o banco de usuários local estiver vazio, reseta os offsets do grupo para earliest."""
# # # #     if UserClient.objects.count() == 0:
# # # #         logger.info("Nenhum usuário local encontrado. Resetando offsets do grupo '%s' para earliest...", GROUP_ID)
# # # #         try:
# # # #             admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
# # # #             # Obtém as partições do tópico
# # # #             meta = admin.describe_topics([TOPIC])[0]
# # # #             partitions = [f"{TOPIC}-{p['partition']}" for p in meta['partitions']]
# # # #             # Define todos os offsets para 0 (earliest)
# # # #             admin.alter_consumer_group_offsets(
# # # #                 group_id=GROUP_ID,
# # # #                 offsets={tp: 0 for tp in partitions}
# # # #             )
# # # #             logger.info("Offsets resetados com sucesso.")
# # # #         except Exception as e:
# # # #             logger.error("Falha ao resetar offsets: %s", e)
# # # #         finally:
# # # #             if 'admin' in locals():
# # # #                 admin.close()
# # # #     else:
# # # #         logger.info("%d usuário(s) já existem no banco local. Offsets mantidos.", UserClient.objects.count())


# # # # # Executa a verificação antes de criar o consumer
# # # # reset_offsets_if_empty()

# # # # consumer = KafkaConsumer(
# # # #     TOPIC,
# # # #     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
# # # #     group_id=GROUP_ID,
# # # #     auto_offset_reset='earliest',
# # # #     value_deserializer=lambda v: json.loads(v.decode('utf-8')),
# # # #     key_deserializer=lambda k: k.decode('utf-8') if k else None,
# # # # )

# # # # logger.info("Consumer iniciado, aguardando mensagens no tópico %s", TOPIC)

# # # # try:
# # # #     for message in consumer:
# # # #         try:
# # # #             user_data = message.value
# # # #             user_id = user_data['id']
# # # #             name = user_data['name']
# # # #             is_rider = user_data.get('is_rider', False)

# # # #             obj, created = UserClient.objects.update_or_create(
# # # #                 id=user_id,
# # # #                 defaults={'name': name, 'is_rider': is_rider}
# # # #             )
# # # #             status = 'criado' if created else 'atualizado'
# # # #             logger.info("Usuário %s (%s) %s com sucesso.", user_id, name, status)
# # # #         except Exception as e:
# # # #             logger.exception("Erro ao processar mensagem: %s", e)
# # # # except KeyboardInterrupt:
# # # #     logger.info("Consumer encerrado.")


# # # import sys
# # # import os

# # # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # # import json
# # # import logging
# # # import uuid
# # # from kafka import KafkaConsumer
# # # import django

# # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# # # django.setup()

# # # from chat_service.models import UserClient

# # # logging.basicConfig(level=logging.INFO)
# # # logger = logging.getLogger(__name__)

# # # KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-user:9092')
# # # TOPIC = 'user-events'

# # # # Gera um group_id fixo ou novo se o banco estiver vazio
# # # if UserClient.objects.count() == 0:
# # #     GROUP_ID = f'chat-service-{uuid.uuid4()}'
# # #     logger.info("Banco vazio. Usando novo grupo: %s", GROUP_ID)
# # # else:
# # #     GROUP_ID = 'chat-service'   # ou um nome fixo se já houver usuários

# # # consumer = KafkaConsumer(
# # #     TOPIC,
# # #     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
# # #     group_id=GROUP_ID,
# # #     auto_offset_reset='earliest',
# # #     value_deserializer=lambda v: json.loads(v.decode('utf-8')),
# # #     key_deserializer=lambda k: k.decode('utf-8') if k else None,
# # # )

# # # logger.info("Consumer iniciado, aguardando mensagens no tópico %s", TOPIC)

# # # try:
# # #     for message in consumer:
# # #         try:
# # #             user_data = message.value
# # #             user_id = user_data['id']
# # #             name = user_data['name']
# # #             is_rider = user_data.get('is_rider', False)

# # #             obj, created = UserClient.objects.update_or_create(
# # #                 id=user_id,
# # #                 defaults={'name': name, 'is_rider': is_rider}
# # #             )
# # #             status = 'criado' if created else 'atualizado'
# # #             logger.info("Usuário %s (%s) %s com sucesso.", user_id, name, status)
# # #         except Exception as e:
# # #             logger.exception("Erro ao processar mensagem: %s", e)
# # # except KeyboardInterrupt:
# # #     logger.info("Consumer encerrado.")



# # import sys
# # import os

# # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # import json
# # import logging
# # import uuid
# # from kafka import KafkaConsumer
# # import django

# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# # django.setup()

# # from chat_service.models import UserClient

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka-user:9092')
# # TOPIC = 'user-events'

# # # Se o banco estiver vazio, gera um novo grupo para forçar a leitura de todas as mensagens
# # if UserClient.objects.count() == 0:
# #     GROUP_ID = f'chat-service-{uuid.uuid4()}'
# #     logger.info("Banco vazio. Usando novo grupo: %s", GROUP_ID)
# # else:
# #     GROUP_ID = 'chat-service'

# # consumer = KafkaConsumer(
# #     TOPIC,
# #     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
# #     group_id=GROUP_ID,
# #     auto_offset_reset='earliest',
# #     value_deserializer=lambda v: json.loads(v.decode('utf-8')),
# #     key_deserializer=lambda k: k.decode('utf-8') if k else None,
# # )

# # logger.info("Consumer iniciado, aguardando mensagens no tópico %s", TOPIC)

# # try:
# #     for message in consumer:
# #         try:
# #             user_data = message.value
# #             user_id = user_data['id']
# #             name = user_data['name']
# #             is_rider = user_data.get('is_rider', False)

# #             obj, created = UserClient.objects.update_or_create(
# #                 id=user_id,
# #                 defaults={'name': name, 'is_rider': is_rider}
# #             )
# #             status = 'criado' if created else 'atualizado'
# #             logger.info("Usuário %s (%s) %s com sucesso.", user_id, name, status)
# #         except Exception as e:
# #             logger.exception("Erro ao processar mensagem: %s", e)
# # except KeyboardInterrupt:
# #     logger.info("Consumer encerrado.")



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

    data = {
        'user_id': str(user_id),
        'message': message,
    }
    try:
        future = prod.send('chat_notifications', key=str(user_id), value=data)
        future.get(timeout=5)
        logger.info("Notificação de chat enviada para %s", user_id)
    except Exception as e:
        logger.error("Falha ao enviar notificação de chat: %s", e)