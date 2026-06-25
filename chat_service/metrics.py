from prometheus_client import Counter

chat_rooms_total = Counter(
    "chat_rooms_total",
    "Total de salas criadas"
)

messages_total = Counter(
    "messages_total",
    "Total de mensagens enviadas"
)

users_chat_total = Counter(
    "users_chat_total",
    "Total de usuarios sincronizados"
)