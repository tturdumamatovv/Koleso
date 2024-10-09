from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.services.get_coordinates import get_coordinates
from .models import Restaurant, Order
from ..services.bonuces import apply_bonus_points
from apps.services.generate_message import format_order_status_change_message
from apps.services.firebase_notification import send_firebase_notification
from apps.authentication.models import User

from decouple import config

api_key=config('API_KEY')

@receiver(pre_save, sender=Restaurant)
def set_coordinates(sender, instance, **kwargs):
    if instance.address and (instance.latitude is None or instance.longitude is None):
        latitude, longitude = get_coordinates(instance.address, api_key)
        if latitude and longitude:
            instance.latitude = latitude
            instance.longitude = longitude
            instance.save()


@receiver(pre_save, sender=Order)
def check_status_change(sender, instance, **kwargs):
    if instance.pk:
        # Получаем старую версию заказа для проверки изменений
        old_order = sender.objects.get(pk=instance.pk)

        # Проверяем, изменился ли статус заказа на 'completed'
        if old_order.order_status != instance.order_status and instance.order_status == 'completed':
            # Обновляем время доставки и последнее время заказа пользователя
            instance.delivery.delivery_time = datetime.now()
            instance.delivery.save()

            instance.user.last_order = datetime.now()
            instance.user.save()

            # Применяем бонусные баллы
            apply_bonus_points(instance.user, instance.total_bonus_amount)

        # Проверяем, существует ли пользователь и есть ли у него FCM токен
        if instance.user and instance.user.fcm_token:
            try:
                # Формируем текст уведомления
                body = format_order_status_change_message(instance.order_time, instance.id, instance.order_status)

                # Отправляем уведомление через Firebase
                send_firebase_notification(
                    token=instance.user.fcm_token,
                    title="Изменение статуса заказа",
                    body=body
                )
            except Exception as e:
                print(f"Ошибка при отправке уведомления: {e}")
        else:
            print(f"Пользователь {instance.user.id if instance.user else 'не указан'} не имеет FCM токена для отправки уведомлений.")


@receiver(post_save, sender=Order)
def notify_collectors_on_order_pending(sender, instance, created, **kwargs):
    if created or instance.order_status == 'pending':  # Только если заказ создан или статус изменен на "pending"
        collectors = User.objects.filter(role='collector')

        body = format_order_status_change_message(order_date=instance.order_time, order_id=instance.id, order_status=instance.order_status)

        for collector in collectors:
            if collector.fcm_token:
                try:
                    title = "Новый заказ в ожидании"
                    send_firebase_notification(token=collector.fcm_token, title=title, body=body)
                except Exception as e:
                    print(f"Ошибка при отправке уведомления сборщику {collector.phone_number}: {e}")


@receiver(post_save, sender=Order)
def notify_couriers_on_order_ready(sender, instance, created, **kwargs):
    # Убедимся, что это обновление заказа и статус изменен на 'ready'
    if not created and instance.order_status == 'ready':
        deliveries = User.objects.filter(role='delivery')

        body = format_order_status_change_message(order_date=instance.order_time, order_id=instance.id, order_status=instance.order_status)

        for delivery in deliveries:
            if delivery.fcm_token:
                try:
                    title = "Новый заказ в ожидании"  # Делаем заголовок одинаковым
                    send_firebase_notification(token=delivery.fcm_token, title=title, body=body)
                except Exception as e:
                    print(f"Ошибка при отправке уведомления курьеру {delivery.phone_number}: {e}")


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "orders_notifications", {
                "type": "send_notification",
                "message": f"Новый заказ №: {instance.id}"
            }
        )
