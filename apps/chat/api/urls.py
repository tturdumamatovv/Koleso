from django.urls import path
from .views import (
    ChatListView,
    SendMessageView,
    GetChatIdView,
    CreateChatView,
    mark_messages_as_read
)

urlpatterns = [
    # URL для получения списка чатов
    path('chats/', ChatListView.as_view(), name='chat-list'),

    # URL для отправки сообщения
    path('chats/send/', SendMessageView.as_view(), name='send-message'),
    path('get-chat-id/', GetChatIdView.as_view(), name='get-chat-id'),

    path('create-chat/', CreateChatView.as_view(), name='create-chat'),
    path('mark-as-read/<int:chat_id>/', mark_messages_as_read, name='mark_messages_as_read'),
]
