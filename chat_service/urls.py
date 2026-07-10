# chat_service/urls.py
from django.urls import path
from .views import RoomDetail, MessageList, RoomListCreate, AdminLogsView

urlpatterns = [
    # Alterado de <int:carona_id> para <uuid:carona_id>
    path('rooms/', RoomListCreate.as_view(), name='room-list-create'),          # novo endpoint
    path('rooms/<uuid:carona_id>/', RoomDetail.as_view(), name='room-detail'),
    path('rooms/<uuid:carona_id>/messages/', MessageList.as_view(), name='message-list'),
    path('admin-logs/', RoomDetail.as_view(), name='room-detail'), # (Suas rotas antigas...)
    path('admin-logs/', AdminLogsView.as_view(), name='chat-admin-logs'),
]