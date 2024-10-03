from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from rest_framework import status

from apps.chat.models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from ...authentication.models import User

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(user=user) if not user.is_staff else Chat.objects.all()


class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        content = self.request.data.get('content')
        image = self.request.FILES.get('image')

        # Get the admin and the current user (either admin or normal user)
        admin = User.objects.filter(is_superuser=True).first()  # Admin
        user = self.request.user  # The current user (sender)

        # Get recipient_id from request data
        recipient_id = self.request.data.get('recipient_id', None)
        recipient = User.objects.get(id=recipient_id) if recipient_id else user

        # Check if a chat already exists between the user and admin
        chat = Chat.objects.filter(user=recipient, admin=admin).first()

        # If chat doesn't exist, create a new one
        if not chat:
            chat = Chat.objects.create(user=recipient, admin=admin)

        # Create and save the message
        message = serializer.save(chat=chat, sender=user, recipient=recipient, content=content, image=image)

        # Send message to Firebase
        self.send_message_to_firebase(chat, message)

    def send_message_to_firebase(self, chat, message):
        from firebase_admin import firestore
        db = firestore.client()

        # Get sender and recipient full names
        sender_full_name = message.sender.full_name if message.sender.full_name else message.sender.phone_number
        recipient_full_name = message.recipient.full_name if message.recipient.full_name else message.recipient.phone_number

        # Structure for the message that includes full names
        message_data = {
            'sender_full_name': sender_full_name,
            'recipient_full_name': recipient_full_name,
            'sender_id': message.sender.id,
            'recipient_id': message.recipient.id,
            'content': message.content,
            'image_url': message.image.url if message.image else None,
            'timestamp': message.timestamp
        }

        # Save the message to Firestore
        db.collection('chats').document(str(chat.id)).collection('messages').add(message_data)

        # Save sender and recipient info in Firestore (if not already saved)
        self.save_user_to_firestore(message.sender)
        self.save_user_to_firestore(message.recipient)

    def save_user_to_firestore(self, user):
        from firebase_admin import firestore
        db = firestore.client()

        user_data = {
            'full_name': user.full_name,
            'phone_number': user.phone_number
        }

        # Add or update user info in Firestore
        user_ref = db.collection('users').document(str(user.id))
        user_ref.set(user_data, merge=True)


class GetChatIdView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        admin_id = request.query_params.get('admin_id')

        try:
            chat = Chat.objects.get(user_id=user_id, admin_id=admin_id)
            return Response({"chat_id": chat.id}, status=status.HTTP_200_OK)
        except Chat.DoesNotExist:
            return Response({"chat_id": None}, status=status.HTTP_200_OK)


class CreateChatView(generics.GenericAPIView):

    class CreateChatSerializer(serializers.Serializer):
        user_id = serializers.IntegerField()
        admin_id = serializers.IntegerField()
        content = serializers.CharField()

    def post(self, request, *args, **kwargs):
        serializer = self.CreateChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data.get('user_id')
        admin_id = serializer.validated_data.get('admin_id')
        content = serializer.validated_data.get('content')

        try:
            admin = User.objects.get(id=admin_id, is_superuser=True)
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Пользователь или администратор не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Находим или создаем чат
        chat, created = Chat.objects.get_or_create(user=user, admin=admin)

        # Создаем сообщение
        message = Message.objects.create(
            chat=chat,
            sender=admin,
            recipient=user,
            content=content
        )

        return Response({"chat_id": chat.id}, status=status.HTTP_201_CREATED)
