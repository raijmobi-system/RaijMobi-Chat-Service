import sys
import os
import json
import logging
import time

# Garante que o diretório raiz do projeto esteja no PATH para o Django localizar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Inicializa o ambiente do Django dentro do script isolado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from kafka import KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError
from chat_service.models import ChatRoom, UserClient
from django.conf import settings

# Configuração básica de logs para acompanhar tudo no terminal do Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Resgata as variáveis de ambiente ou define os fallbacks padrão
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS_RIDE', 'kafka-ride:9092')
TOPIC = 'ride-events'

logger.info("⚡ Iniciando o script do consumidor de caronas...")

# ===================================================================
# LOOP DE RESILIÊNCIA: Aguarda o Broker do Kafka iniciar por completo
# ===================================================================
consumer = None
for tentativa in range(15):
    try:
        logger.info(f"🔄 Conectando ao Kafka em '{KAFKA_BOOTSTRAP_SERVERS}' (Tentativa {tentativa + 1}/15)...")
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id='chat-ride-consumer',
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            request_timeout_ms=5000,
        )
        break  # Conexão estabelecida com sucesso, interrompe o loop de tentativas!
    except (KafkaTimeoutError, KafkaError, Exception) as e:
        logger.warning(f"⚠️ Kafka ainda não está pronto/disponível. Aguardando 5 segundos... Erro: {e}")
        time.sleep(5)

if not consumer:
    logger.critical("❌ FALHA CRÍTICA: Não foi possível estabelecer conexão com o Kafka. Encerrando o serviço.")
    sys.exit(1)

logger.info(f"🚀 Conectado ao Kafka com sucesso! Escutando o tópico '{TOPIC}'...")

# ===================================================================
# LOOP PRINCIPAL: Processamento de Mensagens recebidas
# ===================================================================
try:
    for message in consumer:
        try:
            data = message.value
            logger.info(f"📦 Nova mensagem recebida no Kafka: {data}")

            # Captura e validação estrita dos campos necessários
            ride_id = data.get('ride_id')
            driver_id = data.get('driver_id')
            origin = data.get('origin', 'Desconhecido')
            destination = data.get('destination', 'Desconhecido')
            start_time = data.get('start_time')
            price = data.get('price', '0.00')
            available_seats = data.get('available_seats', 0)

            if not ride_id or not driver_id:
                logger.error("❌ Mensagem corrompida ignorada: 'ride_id' ou 'driver_id' ausentes.")
                continue

            # Garante a existência do motorista na base de dados do chat_service
            driver, driver_created = UserClient.objects.get_or_create(
                id=driver_id, 
                defaults={'name': 'Motorista'}
            )
            if driver_created:
                logger.info(f"👤 Novo motorista espelhado localmente: ID {driver_id}")

            # Cria ou atualiza a sala de chat associada à carona criada
            room, created = ChatRoom.objects.update_or_create(
                carona_id=ride_id,
                defaults={
                    'driver': driver,
                    'origin': origin,
                    'destination': destination,
                    'start_time': start_time,
                    'price': price,
                    'available_seats': available_seats,
                    'ativo': True,
                }
            )
            
            status = 'CRIADA' if created else 'ATUALIZADA'
            logger.info(f"✅ Sala de Chat da carona {ride_id} foi {status} com sucesso no banco local.")

        except KeyError as ke:
            logger.error(f"❌ Erro de mapeamento de chave no payload da mensagem JSON: {ke}")
        except Exception as e:
            logger.exception(f"❌ Falha inesperada ao processar o evento da carona: {e}")

except KeyboardInterrupt:
    logger.info("🛑 Consumer encerrado manualmente via teclado.")
finally:
    if consumer:
        consumer.close()
        logger.info("🔌 Conexões do Kafka fechadas de forma limpa.")