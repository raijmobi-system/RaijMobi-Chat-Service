import sys, os, json, logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from kafka import KafkaConsumer
from chat_service.models import ChatRoom, UserClient
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS_RIDE', 'kafka-ride:9092')
TOPIC = 'ride-events'

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id='chat-ride-consumer',
    auto_offset_reset='earliest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
)

logger.info("Consumer ride-events iniciado. Aguardando mensagens...")

for message in consumer:
    data = message.value
    ride_id = data['ride_id']
    driver_id = data['driver_id']
    origin = data['origin']
    destination = data['destination']
    start_time = data['start_time']
    price = data['price']
    available_seats = data['available_seats']

    # Garante que o motorista exista localmente (via UserClient)
    driver, _ = UserClient.objects.get_or_create(id=driver_id, defaults={'name': 'Motorista'})

    # Cria ou atualiza a sala
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
    status = 'criada' if created else 'atualizada'
    logger.info(f"Sala da carona {ride_id} {status} com sucesso.")