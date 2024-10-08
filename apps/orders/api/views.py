from datetime import datetime
from decimal import Decimal

import requests
from rest_framework import generics, status
from rest_framework.response import Response

from apps.authentication.models import UserAddress
from apps.orders.models import (
    Restaurant,
    TelegramBotToken,
    Order, PromoCode
)
from apps.services.bonuces import (
    calculate_bonus_points,
    apply_bonus_points
)
from apps.services.calculate_bonus import calculate_and_apply_bonus
from apps.services.calculate_delivery_fee import calculate_delivery_fee
from apps.services.calculate_distance import get_distance_between_locations
from apps.services.generate_message import generate_order_message
from apps.services.is_restaurant_open import is_restaurant_open
from apps.services.send_telegram_message import send_telegram_message
from .serializers import (
    OrderSerializer,
    OrderPreviewSerializer,
    ReportSerializer,
    RestaurantSerializer,
    OrderListSerializer,
    OrderDeliverySerializer
)
from ..permissions import IsCollector


class ListOrderView(generics.ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request
        })
        return context


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        if request.data.get('delivery'):
            user_address_id = request.data.get('delivery').get('user_address_id') or None
        else:
            user_address_id = None
        restaurant_id = request.data.get('restaurant_id', None)
        order_source = request.data.get('order_source', 'unknown')
        comment = request.data.get('comment', '')
        promo_code = request.data.get('promo_code', None)
        order_time = datetime.now()
        if user_address_id:
            user_address_instance = UserAddress.objects.get(id=user_address_id, user=user)
        else:
            user_address_instance = 1
        token = TelegramBotToken.objects.first()
        is_pickup = request.data.get('is_pickup', False)

        if not is_pickup and user_address_instance == 1:
            return Response({"error": "User address does not have coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        if not is_pickup:
            user_location = (user_address_instance.latitude, user_address_instance.longitude)
            nearest_restaurant = None
            min_distance = float('inf')

            min_distance, nearest_restaurant = self.get_nearest_restaurant(min_distance, nearest_restaurant, order_time,
                                                                           token, user_location)

            if not nearest_restaurant:
                return Response({"error": "No available restaurants found or all are closed."},
                                status=status.HTTP_400_BAD_REQUEST)

            delivery_fee = calculate_delivery_fee(min_distance)
        else:
            if restaurant_id:
                try:
                    nearest_restaurant = Restaurant.objects.get(id=restaurant_id)
                    if not is_restaurant_open(nearest_restaurant, order_time):
                        return Response({"error": "Selected restaurant is closed."}, status=status.HTTP_400_BAD_REQUEST)
                except Restaurant.DoesNotExist:
                    return Response({"error": "Restaurant not found."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Restaurant ID is required for pickup."}, status=status.HTTP_400_BAD_REQUEST)

            min_distance = 0
            delivery_fee = 0

        serializer = self.add_setializer_context(delivery_fee, nearest_restaurant, request, user)

        self.perform_create(serializer)

        order = serializer.instance
        order.user = self.request.user
        order.comment = comment
        bonus_points = calculate_bonus_points(Decimal(order.total_amount), Decimal(delivery_fee), order_source)
        order.total_bonus_amount = bonus_points

        try:
            total_order_amount = calculate_and_apply_bonus(order)
            order.total_amount = total_order_amount + delivery_fee
            order.promo_code = PromoCode.objects.filter(code=promo_code).first() if promo_code else None

            order.save()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        message = generate_order_message(order, min_distance, delivery_fee)
        order.delivery.distance_km = min_distance
        order.delivery.save()
        print(message)
        bot_token_instance = TelegramBotToken.objects.first()
        if bot_token_instance:
            self.send_order(bot_token_instance, message, nearest_restaurant)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Не установлен токен бота Telegram."}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def send_order(self, bot_token_instance, message, nearest_restaurant):
        telegram_bot_token = bot_token_instance.bot_token
        telegram_chat_ids = nearest_restaurant.get_telegram_chat_ids()
        for chat_id in telegram_chat_ids:
            if chat_id:
                send_telegram_message(telegram_bot_token, chat_id, message)

    def add_setializer_context(self, delivery_fee, nearest_restaurant, request, user):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context['nearest_restaurant'] = nearest_restaurant
        serializer.context['delivery_fee'] = delivery_fee
        serializer.context['user'] = user
        return serializer

    def get_nearest_restaurant(self, min_distance, nearest_restaurant, order_time, token, user_location):
        for restaurant in Restaurant.objects.all():
            if restaurant.latitude and restaurant.longitude:
                restaurant_location = (restaurant.latitude, restaurant.longitude)
                distance = get_distance_between_locations(token.google_map_api_key, user_location,
                                                          restaurant_location)
                if distance is not None and distance < min_distance and is_restaurant_open(restaurant, order_time):
                    min_distance = distance
                    nearest_restaurant = restaurant
        return min_distance, nearest_restaurant


class OrderPreviewView(generics.GenericAPIView):
    serializer_class = OrderPreviewSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        order_time = datetime.now()
        user_address_id = data.get('user_address_id')
        is_pickup = data.get('is_pickup', False)

        try:
            user_address_instance = UserAddress.objects.get(id=user_address_id, user=user)
        except UserAddress.DoesNotExist:
            return Response({"error": "User address does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if not is_pickup and (not user_address_instance.latitude or not user_address_instance.longitude):
            return Response({"error": "User address does not have coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        nearest_restaurant = None
        min_distance = float('inf')
        delivery_fee = 0

        if not is_pickup:
            user_location = (user_address_instance.latitude, user_address_instance.longitude)

            for restaurant in Restaurant.objects.all():
                if restaurant.latitude and restaurant.longitude:
                    restaurant_location = (restaurant.latitude, restaurant.longitude)
                    distance = get_distance_between_locations('AIzaSyCWbO5aOn8hS3EWJycj73dHqH8fHHfO4w4', user_location,
                                                              restaurant_location)
                    if distance is not None and distance < min_distance and is_restaurant_open(restaurant, order_time):
                        min_distance = distance
                        nearest_restaurant = restaurant

            if not nearest_restaurant:
                return Response({"error": "No available restaurants found or all are closed."},
                                status=status.HTTP_400_BAD_REQUEST)

            delivery_fee = calculate_delivery_fee(min_distance)

        response_data = self.prepare_response(delivery_fee, is_pickup, min_distance)

        return Response(response_data, status=status.HTTP_200_OK)

    def prepare_response(self, delivery_fee, is_pickup, min_distance):
        response_data = {

            "delivery_info": {
                "distance_km": min_distance,
                "delivery_fee": delivery_fee
            } if not is_pickup else None,

        }
        return response_data


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs):
        report, serializer = self.create_report(request)

        self.send_report_to_telegram(report)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def create_report(self, request):
        description = request.data.get('description')
        contact_number = request.data.get('contact_number')
        image = request.FILES.get('image') if 'image' in request.FILES else None
        report_data = {
            'description': description,
            'contact_number': contact_number,
            'image': image
        }
        serializer = self.get_serializer(data=report_data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        return report, serializer

    def send_report_to_telegram(self, report):
        bot_token_instance = TelegramBotToken.objects.first()
        if not bot_token_instance:
            print("Токен бота Telegram не настроен.")
            return

        telegram_bot_token = bot_token_instance.bot_token
        telegram_chat_ids = bot_token_instance.report_channels.split(',')

        message = f"Новый репорт:\nОписание: {report.description}\nКонтактный номер: {report.contact_number}"

        self.send_report_to_chats(message, report, telegram_bot_token, telegram_chat_ids)

    def send_report_to_chats(self, message, report, telegram_bot_token, telegram_chat_ids):
        for chat_id in telegram_chat_ids:
            chat_id = chat_id.strip()
            message_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            photo_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendPhoto"

            message_payload = {
                'chat_id': chat_id,
                'text': message
            }
            response = requests.post(message_url, data=message_payload)
            if response.status_code != 200:
                print(f"Ошибка при отправке сообщения в чат {chat_id}: {response.text}")

            if report.image:
                with report.image.open('rb') as image_file:
                    files = {'photo': image_file}
                    photo_payload = {'chat_id': chat_id}
                    response = requests.post(photo_url, data=photo_payload, files=files)
                    if response.status_code == 200:
                        print(f"Фотография отправлена в чат {chat_id}")
                    else:
                        print(f"Ошибка при отправке фотографии в чат {chat_id}: {response.text}")


class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class CollectorOrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]

    def get_queryset(self):
        # Получаем заказы для сборщика
        return Order.objects.filter(order_status__in=['pending', 'in_progress'])


class CollectorOrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]

    def patch(self, request, *args, **kwargs):
        # Меняем статус заказа на "Готово"
        order_id = kwargs.get('pk')
        try:
            order = Order.objects.get(pk=order_id)
            if order.order_status in ['pending', 'in_progress']:
                order.order_status = 'ready'
                order.save()
                return Response({'status': 'success', 'message': 'Заказ обновлен до статуса "Готово".'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'Невозможно обновить заказ в текущем статусе.'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'status': 'error', 'message': 'Заказ не найден.'}, status=status.HTTP_404_NOT_FOUND)


class CourierOrderReadyListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]  # Только для курьеров

    def get_queryset(self):
        # Фильтруем заказы со статусом "Готово"
        return Order.objects.filter(order_status='ready')


class CourierPickOrderView(generics.UpdateAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        user = request.user
        try:
            order = Order.objects.get(pk=order_id)
            if order.order_status == 'ready':
                order.order_status = 'delivery'  # Изменяем статус на "В процессе"
                order.courier = user
                order.save()
                return Response({'status': 'success', 'message': 'Заказ взят в обработку.'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'Невозможно взять заказ, который не готов.'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'status': 'error', 'message': 'Заказ не найден.'}, status=status.HTTP_404_NOT_FOUND)


class CourierOrderDeliverListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]  # Только для курьеров

    def get_queryset(self):
        # Фильтруем заказы со статусом "Готово"
        return Order.objects.filter(order_status='delivery')


class CourierCompleteOrderView(generics.UpdateAPIView):
    serializer_class = OrderDeliverySerializer
    permission_classes = [IsCollector]  # Только для курьеров

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(pk=order_id)
            if order.order_status == 'delivery':  # Только если заказ в пути
                order.order_status = 'completed'  # Меняем статус на завершен
                order.delivery_photo = serializer.validated_data.get('delivery_photo')
                order.delivery_comment = serializer.validated_data.get('delivery_comment')
                order.save()
                return Response({'status': 'success', 'message': 'Заказ успешно завершен.'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'Невозможно завершить заказ, который не в пути.'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'status': 'error', 'message': 'Заказ не найден.'}, status=status.HTTP_404_NOT_FOUND)


class CourierOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]

    def get_queryset(self):
        # Возвращаем только заказы, которые были взяты текущим курьером
        return Order.objects.filter(courier=self.request.user).order_by('-order_time')


class CollectorOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]

    def get_queryset(self):
        # Возвращаем только заказы, которые были взяты текущим курьером
        return Order.objects.filter(collector=self.request.user).order_by('-order_time')
