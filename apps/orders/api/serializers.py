import pytz

from django.db import transaction
from django.conf import settings

from rest_framework import serializers

from apps.authentication.models import UserAddress, User
from apps.orders.models import (
    Order,
    OrderItem,
    Delivery,
    Topping,
    Restaurant,
    Report,
    TelegramBotToken, PromoCode

)  # Ingredient)


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone_number', 'email', 'opening_hours', 'closing_hours',
                  'latitude', 'longitude', 'self_pickup_available']


class ProductOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(read_only=True)
    product_size_id = serializers.IntegerField(write_only=True)
    topping_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    quantity = serializers.IntegerField(default=0)
    is_bonus = serializers.BooleanField(default=False)

    # excluded_ingredient_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = OrderItem
        fields = ['product_size_id', 'quantity', 'topping_ids', 'is_bonus', 'product']  # , 'excluded_ingredient_ids'

    def validate(self, data):
        if data.get('product_size_id') == 0:
            raise serializers.ValidationError("Invalid product_size_id.")
        return data

    def get_product(self, obj):
        request = self.context.get('request')
        photo_url = obj.product_size.product.photo.url if obj.product_size.product.photo else None
        if photo_url and request:
            photo_url = request.build_absolute_uri(photo_url)

        product_exists = obj.product_size.product.__class__.objects.filter(pk=obj.product_size.product.pk).exists()

        return {
            'name': obj.product_size.product.name,
            'description': obj.product_size.product.description,
            'price': obj.product_size.get_price(),
            'image': photo_url,
            'product_size': obj.product_size.size,
            'product_size_id': obj.product_size.id,
            'in_stock': product_exists
        }


# class SetOrderItemSerializer(serializers.ModelSerializer):
#     set_id = serializers.IntegerField(write_only=True)
#
#     class Meta:
#         model = OrderItem
#         fields = ['set_id', 'quantity', 'is_bonus']
#
#     def validate(self, data):
#         if data.get('set_id') == 0:
#             raise serializers.ValidationError("Invalid set_id.")
#         return data
#

class DeliverySerializer(serializers.ModelSerializer):
    user_address_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Delivery
        fields = ['user_address_id']


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'full_name']


class OrderListSerializer(serializers.ModelSerializer):
    order_items = ProductOrderItemSerializer(many=True, required=False)
    restaurant = RestaurantSerializer()
    total_amount = serializers.SerializerMethodField()
    delivery_fee = serializers.SerializerMethodField()
    order_time = serializers.SerializerMethodField()
    user_address = serializers.SerializerMethodField()
    app_download_url = serializers.SerializerMethodField()
    user = UserSummarySerializer()
    order_status = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    order_source = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'payment_method', 'delivery_fee', 'change', 'order_time', 'restaurant', 'order_items', 'total_bonus_amount',
                  'is_pickup', 'user_address', 'app_download_url', 'order_status', 'user', 'comment', 'order_source']

    def get_total_amount(self, obj):
        return obj.get_total_amount_2()

    def get_delivery_fee(self, obj):
        return obj.delivery.delivery_fee if obj.delivery else 0

    def get_order_time(self, obj):
        local_tz = pytz.timezone(settings.TIME_ZONE)
        order_time = obj.order_time.astimezone(local_tz)
        return order_time.strftime('%Y-%m-%d %H:%M')

    def get_user_address(self, obj):
        return obj.delivery.user_address.city if obj.delivery.user_address else "Самовывоз"

    def get_app_download_url(self, obj):
        link = TelegramBotToken.objects.first().app_download_link
        if not link:
            return None
        return link

    def get_order_status(self, obj):
        status_map = {
            'pending': 'В ожидании',
            'in_progress': 'В процессе',
            'delivery': 'Доставка',
            'completed': 'Завершено',
            'cancelled': 'Отменено',
            'ready': 'Готово',
        }
        return status_map.get(obj.order_status, obj.order_status)  # Поле app_download_link было связано с моделью TelegramBotToken, которая была удалена

    def get_payment_method(self, obj):
        status_map = {
            'cash': 'Наличкой',
            'card': 'Картой'
        }
        return status_map.get(obj.payment_method, obj.payment_method)

    def get_order_source(self, obj):
        status_map = {
            'web': 'Веб Сайт',
            'mobile': 'Мобильное Приложение'
        }
        return status_map.get(obj.order_source, obj.order_source)


class OrderDeliverySerializer(serializers.ModelSerializer):
    delivery_photo = serializers.ImageField(required=True)
    delivery_comment = serializers.CharField(required=True)

    class Meta:
        model = Order
        fields = ['delivery_photo', 'delivery_comment', 'order_status']


class OrderSerializer(serializers.ModelSerializer):
    products = ProductOrderItemSerializer(many=True, required=False)
    # sets = SetOrderItemSerializer(many=True, required=False)
    restaurant_id = serializers.IntegerField(required=False, allow_null=True)
    delivery = DeliverySerializer(required=False)
    order_source = serializers.ChoiceField(choices=[('web', 'web'), ('mobile', 'mobile')], default='web')
    change = serializers.IntegerField(default=0)
    is_pickup = serializers.BooleanField(default=False)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    partial_bonus_amount = serializers.DecimalField(max_digits=9, decimal_places=2, required=False)

    class Meta:
        model = Order
        fields = [
            'id', 'delivery', 'order_time', 'total_amount', 'is_pickup',
            'order_status', 'products', 'payment_method', 'change',
            'restaurant_id', 'order_source', 'comment', 'promo_code',
            'partial_bonus_amount'
            # 'sets',
        ]
        read_only_fields = ['total_amount', 'order_time', 'order_status']

    def validate_partial_bonus_amount(self, value):
        user = self.context['user']
        if user.bonus < value:
            raise serializers.ValidationError("Недостаточно бонусов для оплаты.")
        return value

    def create(self, validated_data):
        print(validated_data)
        products_data = validated_data.pop('products', [])
        promo_code_data = validated_data.pop('promo_code', None)

        sets_data = validated_data.pop('sets', [])
        if validated_data.get('delivery'):
            delivery_data = validated_data.pop('delivery')
            user_address = UserAddress.objects.get(id=delivery_data['user_address_id'])

        else:
            delivery_data = {}
            user_address = None
        # user = validated_data.pop('user')

        nearest_restaurant = self.context['nearest_restaurant']
        delivery_fee = self.context['delivery_fee']

        with transaction.atomic():
            delivery = Delivery.objects.create(
                restaurant=nearest_restaurant,
                user_address=user_address if user_address else None,
                delivery_time=delivery_data['delivery_time'] if 'delivery_time' in delivery_data else None,
                delivery_fee=delivery_fee
            )


            order = Order.objects.create(
                delivery=delivery,
                # user=user,
                restaurant=nearest_restaurant,
                **validated_data
            )
            if promo_code_data:
                promo_code_instance = PromoCode.objects.filter(code=promo_code_data).first()
                if not promo_code_instance or not promo_code_instance.is_valid():
                    raise serializers.ValidationError({"promo_code": "Промокод недействителен или его срок истек."})
                validated_data['promo_code'] = promo_code_instance
            else:
                validated_data['promo_code'] = None

            for product_data in products_data:
                topping_ids = product_data.pop('topping_ids', [])
                excluded_ingredient_ids = product_data.pop('excluded_ingredient_ids', [])

                order_item = OrderItem(order=order, product_size_id=product_data['product_size_id'],
                                       quantity=product_data['quantity'], is_bonus=product_data['is_bonus'])

                if topping_ids:
                    toppings = Topping.objects.filter(id__in=topping_ids)
                    order_item.save()  # Сохраняем объект перед установкой связей ManyToMany
                    order_item.topping.set(toppings)  # Устанавливаем начинки

                else:
                    order_item.save()
                # if excluded_ingredient_ids:
                #     excluded_ingredients = Ingredient.objects.filter(id__in=excluded_ingredient_ids)
                #     order_item.excluded_ingredient.set(excluded_ingredients)

            # for set_data in sets_data:
            #     set_order_item = OrderItem(order=order, set_id=set_data['set_id'], quantity=set_data['quantity'])
            #     set_order_item.save()

        return order


class ProductOrderItemPreviewSerializer(serializers.Serializer):
    product_size_id = serializers.IntegerField(write_only=True)
    topping_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    excluded_ingredient_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    quantity = serializers.IntegerField()


# class SetOrderItemPreviewSerializer(serializers.Serializer):
#     set_id = serializers.IntegerField(write_only=True)
#     quantity = serializers.IntegerField()


class OrderPreviewSerializer(serializers.Serializer):
    user_address_id = serializers.IntegerField()


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['image', 'description', 'contact_number']


class CancelOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_status']
