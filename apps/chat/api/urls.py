from django.urls import path
from .views import ChatListView, SendMessageView, GetChatIdView, CreateChatView

urlpatterns = [
    # URL для получения списка чатов
    path('chats/', ChatListView.as_view(), name='chat-list'),

    # URL для отправки сообщения
    path('chats/send/', SendMessageView.as_view(), name='send-message'),
    path('get-chat-id/', GetChatIdView.as_view(), name='get-chat-id'),

    path('create-chat/', CreateChatView.as_view(), name='create-chat'),
]
