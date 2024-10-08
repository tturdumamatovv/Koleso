from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from firebase_admin import firestore

from apps.authentication.models import User
from apps.chat.models import Chat


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_chat_with_admin(sender, instance, created, **kwargs):
    # Подключаемся к Firestore
    db = firestore.client()

    # Данные пользователя для Firestore
    user_data = {
        'full_name': instance.full_name,
        'phone_number': instance.phone_number
    }

    # Добавляем или обновляем информацию о пользователе в Firestore
    user_ref = db.collection('users').document(str(instance.id))
    user_ref.set(user_data, merge=True)

    if created:
        # Логирование создания пользователя
        print(f"Новый пользователь создан и добавлен в Firestore: {user_data}")

        # Находим администратора (можно выбрать первого суперпользователя)
        admin = User.objects.filter(is_superuser=True).first()

        # Если админ существует и новый пользователь — это не сам админ
        if admin and admin.id != instance.id:
            # Проверяем, существует ли уже чат с этим пользователем и админом
            existing_chat = Chat.objects.filter(user=instance, admin=admin).exists()

            if not existing_chat:
                # Создаем новый чат между пользователем и админом
                new_chat = Chat.objects.create(user=instance, admin=admin)

                # Логируем создание чата
                print(f"Создан новый чат между пользователем {instance.full_name} и админом {admin.full_name}")

                # Отправляем информацию о новом чате в Firestore
                chat_data = {
                    'user_id': instance.id,
                    'admin_id': admin.id,
                    'created_at': new_chat.created_at
                }

                # Добавляем или обновляем информацию о чате в Firestore
                chat_ref = db.collection('chats').document(str(new_chat.id))
                chat_ref.set(chat_data, merge=True)

            else:
                print(f"Чат уже существует между пользователем {instance.full_name} и админом {admin.full_name}")

    else:
        # Логирование обновления данных пользователя
        print(f"Данные пользователя обновлены в Firestore: {user_data}")
