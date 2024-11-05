import requests
import logging

from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404

import xml.etree.ElementTree as ET

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from apps.authentication.models import UserAddress, BlacklistedAddress
from apps.orders.models import (
    Restaurant,
    TelegramBotToken,
    Order, PromoCode, OrderItem
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
    OrderDeliverySerializer,
    CancelOrderSerializer
)
from ..freedompay import generate_signature
from ..permissions import IsCollector
from ...product.models import ProductSize

from apps.pages.models import PaymentSettings

# Загрузка настроек
payment_settings = PaymentSettings.objects.first()
if payment_settings:
    PAYBOX_URL = payment_settings.paybox_url
    PAYBOX_MERCHANT_ID = payment_settings.merchant_id
else:
    PAYBOX_URL = ''
    PAYBOX_MERCHANT_ID = ''


logger = logging.getLogger(__name__)


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

def get_user_orders(request):
    user_id = request.GET.get('user_id')
    orders = Order.objects.filter(user_id=user_id).values(
        'id', 'order_time', 'total_amount', 'order_status'
    ).order_by('-id')
    for order in orders:
        order['order_time'] = localtime(order['order_time']).strftime('%d/%m/%Y, %H:%M')
        order['order_status'] = dict(Order._meta.get_field('order_status').choices)[order['order_status']]

    return JsonResponse({'orders': list(orders)}, safe=False)


def get_order_details(request):
    order_id = request.GET.get('order_id')
    try:
        order = get_object_or_404(Order, id=order_id)

        # Используем сериализатор для преобразования данных заказа
        serializer = OrderListSerializer(order, context={'request': request})

        # Преобразуем сериализованные данные в JSON
        order_data = JSONRenderer().render(serializer.data)

        return JsonResponse(serializer.data, safe=False)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        partial_bonus_amount = Decimal(request.data.get('partial_bonus_amount', '0'))

        user.bonus = user.bonus or Decimal('0')

        # Проверка на достаточное количество бонусов
        if partial_bonus_amount > user.bonus:
            return Response({"error": "Недостаточно бонусов для оплаты."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Получение информации о доставке
        delivery_data = request.data.get('delivery')
        user_address_id = delivery_data.get('user_address_id') if delivery_data else None
        restaurant_id = request.data.get('restaurant_id', None)
        order_source = request.data.get('order_source', 'unknown')
        comment = request.data.get('comment', '')
        promo_code = request.data.get('promo_code', None)
        order_time = datetime.now()
        payment_method = request.data.get('payment_method', 'cash')  # По умолчанию 'наличные'

        # Проверка на существование адреса пользователя
        user_address_instance = None
        if user_address_id:
            try:
                user_address_instance = UserAddress.objects.get(id=user_address_id, user=user)
                if BlacklistedAddress.objects.filter(address=user_address_instance).exists():
                    return Response({"error": "Данный адрес находится в черном списке. Заказ нельзя оформить."},
                                    status=status.HTTP_400_BAD_REQUEST)
            except UserAddress.DoesNotExist:
                return Response({"error": "Адрес пользователя не найден."}, status=status.HTTP_400_BAD_REQUEST)

        # Определение координат и расчёт расстояния для доставки
        is_pickup = request.data.get('is_pickup', False)
        nearest_restaurant = None
        min_distance = 0
        delivery_fee = 0

        if not is_pickup and user_address_instance:
            user_location = (user_address_instance.latitude, user_address_instance.longitude)
            min_distance, nearest_restaurant = self.get_nearest_restaurant(
                float('inf'), None, order_time, TelegramBotToken.objects.first(), user_location
            )
            if not nearest_restaurant:
                return Response({"error": "Нет доступных ресторанов или все закрыты."},
                                status=status.HTTP_400_BAD_REQUEST)
            delivery_fee = calculate_delivery_fee(min_distance)
        elif is_pickup:
            if restaurant_id:
                try:
                    nearest_restaurant = Restaurant.objects.get(id=restaurant_id)
                    if not is_restaurant_open(nearest_restaurant, order_time):
                        return Response({"error": "Выбранный ресторан закрыт."},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Restaurant.DoesNotExist:
                    return Response({"error": "Ресторан не найден."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "ID ресторана требуется для самовывоза."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Создание сериализатора с полным контекстом
        serializer = self.get_serializer(
            data=request.data,
            context={'user': user, 'nearest_restaurant': nearest_restaurant, 'delivery_fee': delivery_fee}
        )
        serializer.is_valid(raise_exception=True)

        # Сохранение заказа и применение бонусной суммы
        order = serializer.save(user=user)
        order.partial_bonus_amount = partial_bonus_amount
        order.total_amount = order.calculate_total_after_bonus()
        order.save()

        # Снижение бонусов у пользователя
        user.bonus -= partial_bonus_amount
        user.save()

        response_data = serializer.data
        response_data['total_after_bonus'] = str(order.total_amount)

        # Подготовка продуктов и проверка доступности количества
        for item in request.data.get('products', []):
            product_size_id = item.get('product_size_id')
            ordered_quantity = Decimal(item.get('quantity'))
            try:
                product_size = ProductSize.objects.get(id=product_size_id)
                product = product_size.product

                # Конвертация заказанного количества в кг, если требуется
                quantity_in_kg = self.convert_quantity_to_kg(product_size, ordered_quantity)

                # Проверка на наличие достаточного количества
                if product.quantity < quantity_in_kg:
                    return Response({"error": f"Недостаточно товара для {product.name}."},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Уменьшение количества товара
                product.quantity -= quantity_in_kg
                product.save()

            except ProductSize.DoesNotExist:
                return Response({"error": f"Продукт с указанным размером не найден."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Применение промокода, если имеется
        order.promo_code = PromoCode.objects.filter(code=promo_code).first() if promo_code else None
        order.comment = comment
        bonus_points = calculate_bonus_points(order.total_amount, order_source)
        order.total_bonus_amount = bonus_points

        try:
            # Перерасчет и применение бонусов
            total_order_amount = calculate_and_apply_bonus(order)
            order.total_amount = total_order_amount
            order.save()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Генерация и отправка сообщения о заказе
        message = generate_order_message(order, min_distance, delivery_fee)
        order.delivery.distance_km = min_distance
        order.delivery.save()
        bot_token_instance = TelegramBotToken.objects.first()
        if bot_token_instance:
            self.send_order(bot_token_instance, message, nearest_restaurant)

        # Обработка оплаты, если метод "карта"
        response_data = serializer.data
        if payment_method == "card":
            payment_url = self.create_freedompay_payment(order, user.email, user.phone_number,
                                                         PaymentSettings.objects.first())
            if not payment_url:
                return Response({"error": "Ошибка создания ссылки на оплату."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_data['freedompay_url'] = payment_url

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def convert_quantity_to_kg(self, product_size, ordered_quantity):
        """Конвертирует количество продукта в килограммы, если это необходимо."""
        if product_size.unit == 'g':
            return product_size.quantity * ordered_quantity / Decimal('1000')
        elif product_size.unit == 'kg':
            return product_size.quantity * ordered_quantity
        elif product_size.unit == 'ml':
            return product_size.quantity * ordered_quantity / Decimal('1000')
        elif product_size.unit == 'l':
            return ordered_quantity
        else:
            return ordered_quantity

    def send_order(self, bot_token_instance, message, nearest_restaurant):
        telegram_bot_token = bot_token_instance.bot_token
        telegram_chat_ids = nearest_restaurant.get_telegram_chat_ids()
        for chat_id in telegram_chat_ids:
            if chat_id:
                send_telegram_message(telegram_bot_token, chat_id, message)

    def get_nearest_restaurant(self, min_distance, nearest_restaurant, order_time, token, user_location):
        """Находит ближайший открытый ресторан."""
        for restaurant in Restaurant.objects.all():
            if restaurant.latitude and restaurant.longitude:
                restaurant_location = (restaurant.latitude, restaurant.longitude)
                distance = get_distance_between_locations(token.google_map_api_key, user_location, restaurant_location)
                if distance is not None and distance < min_distance and is_restaurant_open(restaurant, order_time):
                    min_distance = distance
                    nearest_restaurant = restaurant
        return min_distance, nearest_restaurant

    def create_freedompay_payment(self, order, email, phone_number, payment_settings):
        """Создает ссылку на оплату через FreedomPay."""
        url = f"{payment_settings.paybox_url}/init_payment.php"
        amount = order.calculate_total_after_bonus()
        order_id = order.id
        params = {
            'pg_merchant_id': payment_settings.merchant_id,
            'pg_order_id': order_id,
            'pg_amount': amount,
            'pg_currency': 'KGS',
            'pg_description': f"Оплата заказа #{order_id}",
            'pg_user_phone': phone_number,
            'pg_user_contact_email': email,
            'pg_result_url': 'https://koleso.kg/',
            'pg_success_url': 'https://koleso.kg/success/',
            'pg_failure_url': 'https://koleso.kg/failure/',
            'pg_testing_mode': 1,
            'pg_salt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        params['pg_sig'] = generate_signature(params, 'init_payment.php')

        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            response_text = response.text
            root = ET.fromstring(response_text)
            payment_url = root.find('pg_redirect_url')
            return payment_url.text if payment_url is not None else None
        except (ET.ParseError, requests.RequestException) as e:
            print(f"Error during request to Paybox: {e}")
            return None


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

            delivery_fee = str(calculate_delivery_fee(min_distance)) + ' мин'

        response_data = self.prepare_response(delivery_fee, is_pickup, min_distance)

        return Response(response_data, status=status.HTTP_200_OK)

    def prepare_response(self, delivery_fee, is_pickup, min_distance):
        response_data = {

            "delivery_info": {
                "distance_km": min_distance,
                "delivery_fee": 0,
                "delivery_time": delivery_fee,
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
        return Order.objects.filter(order_status__in=['pending', 'in_progress']).order_by('-order_time')


class CollectorOrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsCollector]

    def patch(self, request, *args, **kwargs):
        # Меняем статус заказа на "Готово"
        order_id = kwargs.get('pk')
        user = request.user
        try:
            order = Order.objects.get(pk=order_id)
            if order.order_status in ['pending', 'in_progress']:
                order.order_status = 'ready'
                order.collector = user
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
        return Order.objects.filter(order_status='ready', is_pickup=False).order_by('-order_time')


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
        return Order.objects.filter(order_status='delivery', courier=self.request.user).order_by('-order_time')


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
        # Логируем идентификатор текущего пользователя
        print(f"Текущий пользователь: {self.request.user.id}")

        # Возвращаем только заказы, в которых указан текущий сборщик
        queryset = Order.objects.filter(collector=self.request.user).order_by('-order_time')

        # Логируем количество заказов, найденных для текущего пользователя
        print(f"Найдено заказов для сборщика: {queryset.count()}")

        return queryset


class CancelOrderView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CancelOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')

        # Retrieve the order
        order = get_object_or_404(self.get_queryset(), pk=order_id)
        logger.info(f"Attempting to cancel order #{order.id}")

        # Prevent cancellation if the order is already completed
        if order.order_status == 'completed':
            logger.warning(f"Order #{order.id} is completed and cannot be cancelled.")
            return Response(
                {'error': 'You cannot cancel an order that has been delivered.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем статус заказа на "отменен" и сохраняем, восстановление будет обрабатываться в сигналах
        order.order_status = 'cancelled'
        order.save()
        logger.info(f"Order #{order.id} status updated to 'cancelled'.")

        return Response(
            {'status': 'success', 'message': 'Order has been cancelled, stock quantities and bonus points will be restored.'},
            status=status.HTTP_200_OK
        )