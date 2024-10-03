from rest_framework import serializers

from apps.chat.models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)  # Добавляем роль отправителя
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Message
        fields = ['chat', 'sender', 'sender_name', 'sender_role', 'recipient', 'content', 'image', 'timestamp']
        read_only_fields = ['sender', 'recipient', 'timestamp', 'sender_name', 'sender_role']
        extra_kwargs = {
            'chat': {'required': False}  # Поле chat теперь необязательно
        }


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'user', 'admin', 'created_at', 'messages']
