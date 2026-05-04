from django.urls import path
from .views import RoomDetail, MessageList

urlpatterns = [
    path('rooms/<int:carona_id>/', RoomDetail.as_view(), name='room-detail'),
    path('rooms/<int:carona_id>/messages/', MessageList.as_view(), name='message-list'),
]