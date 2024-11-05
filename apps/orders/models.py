from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from geopy.distance import geodesic
from django.core.validators import MinLengthValidator

from apps.authentication.models import UserAddress, User
from apps.pages.models import SingletonModel
from apps.product.models import ProductSize, Topping  # Set,Ingredient
import random
import string


class WhatsAppChat(SingletonModel):
    whatsapp_number = models.CharField(max_length=200, unique=True, verbose_name=_("Телеграм Бот Токен"))
    def __str__(self):
        return f"{self.whatsapp_number}"

    class Meta:
        verbose_name = _("Номер WhatsApp")
        verbose_name_plural = _("Номер WhatsApp")


class TelegramBotToken(models.Model):
    bot_token = models.CharField(max_length=200, unique=True, verbose_name=_("Телеграм Бот Токен"), null=True, blank=True)
    report_channels = models.TextField(max_length=200, blank=True, null=True, verbose_name=_("Айди каналов"))
    app_download_link = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Ссылка на приложение"))
    google_map_api_key = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Ключ для карты"))

    def clean(self):
        if TelegramBotToken.objects.exists() and not self.pk:
            raise ValidationError(_('Может существовать только один экземпляр модели TelegramBotToken.'))

    def save(self, *args, **kwargs):
        self.pk = 1  # Гарантирует, что всегда существует только один экземпляр
        super().save(*args, **kwargs)

    def __str__(self):
        return "Ключ для карты"

    class Meta:
        verbose_name = _("Токен бота Telegram")
        verbose_name_plural = _("Токены бота Telegram")


class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    address = models.CharField(max_length=255, verbose_name=_('Адрес'))
    phone_number = models.CharField(max_length=15, verbose_name=_('Телефонный номер'), blank=True, null=True)
    email = models.EmailField(verbose_name=_('Электронная почта'), blank=True, null=True)
    opening_hours = models.TimeField(verbose_name=_('Время открытия'), blank=True, null=True)
    closing_hours = models.TimeField(verbose_name=_('Время закрытия'), blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Широта'), blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Долгота'), blank=True, null=True)
    telegram_chat_ids = models.TextField(verbose_name=_('Telegram Chat IDs'), validators=[MinLengthValidator(1)],
                                         help_text=_('Введите чат-айди через запятую'), blank=True, null=True)
    self_pickup_available = models.BooleanField(default=True, verbose_name=_('Самовывоз доступен'))

    class Meta:
        verbose_name = _("Склад")
        verbose_name_plural = _("Склады")

    def __str__(self):
        return self.name

    def get_telegram_chat_ids(self):
        if self.telegram_chat_ids:
            return [chat_id.strip() for chat_id in self.telegram_chat_ids.split(',') if chat_id.strip()]
        return []

    def distance_to(self, user_lat, user_lon):
        restaurant_location = (self.latitude, self.longitude)
        user_location = (user_lat, user_lon)
        return geodesic(restaurant_location, user_location).kilometers


class Delivery(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name=_('Ресторан'))
    user_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, verbose_name=_('Адрес пользователя'),
                                     blank=True, null=True)
    delivery_time = models.DateTimeField(verbose_name=_('Время доставки'), blank=True, null=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Стоимость доставки')
                                       , blank=True, null=True)
    distance_km = models.CharField(max_length=10, verbose_name=_('Расстояние (км)'), blank=True, null=True)

    class Meta:
        verbose_name = _("Доставка")
        verbose_name_plural = _("Доставки")

    def __str__(self):
        return f" {'Доставка ' + self.user_address.city if self.user_address else 'Самовывоз'} от {self.restaurant.name}"


class Order(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name=_('Склад'))
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, verbose_name=_('Доставка'), blank=True, null=True)
    order_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Время заказа'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Общая сумма'), blank=True,
                                       null=True)
    total_bonus_amount = models.IntegerField(verbose_name=_('Общая сумма бонусов'), blank=True, null=True)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='orders', verbose_name=_('Пользователь')
                             , blank=True, null=True)
    is_pickup = models.BooleanField(default=False, verbose_name=_('Самовывоз'))
    payment_method = models.CharField(
        max_length=255,
        choices=[('card', 'Карта'),
                 ('cash', 'Наличные'),
                 ('online', 'Онлайн'),
                 ],
        default='card',
        verbose_name=_('Способ оплаты')
    )
    change = models.IntegerField(verbose_name=_('Сдача'), blank=True, null=True)

    order_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('В ожидании')),
            ('in_progress', _('В процессе')),
            ('delivery', _('Доставка')),
            ('completed', _('Завершено')),
            ('cancelled', _('Отменено')),
            ('ready', _('Готово')),
        ],
        default='pending',
        verbose_name=_('Статус заказа')
    )
    order_source = models.CharField(
        max_length=10,
        choices=[
            ('mobile', 'Мобильное приложение'),
            ('web', 'Веб-сайт'),
            ('unknown', 'Неизвестно')
        ],
        default='unknown',
        verbose_name=_('Источник заказа')
    )
    comment = models.TextField(verbose_name=_('Комментарий'), blank=True, null=True)

    promo_code = models.ForeignKey('PromoCode', on_delete=models.SET_NULL, null=True, blank=True)
    delivery_photo = models.ImageField(upload_to='delivery_photos/', blank=True, null=True,
                                       verbose_name=_('Фото доставки'))
    delivery_comment = models.TextField(blank=True, null=True, verbose_name=_('Комментарий курьера'))
    courier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='courier_orders', verbose_name=_('Курьер'))
    collector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='collector_orders', verbose_name=_('Сборщик'))
    partial_bonus_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0,
                                               verbose_name=_('Частичная оплата бонусами'))
    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f"Заказ #{self.id}"

    def apply_promo_code(self):
        if self.promo_code:
            # Преобразуем процент скидки в Decimal перед расчетом
            discount_rate = Decimal(self.promo_code.discount) / Decimal(100)
            discount_amount = discount_rate * self.total_amount
            return self.total_amount - discount_amount
        return self.total_amount

    def get_total_amount(self):
        total_amount = 0
        for order_item in self.order_items.all():
            total_amount += order_item.total_amount
        return total_amount

    def get_total_amount_2(self):
        total_amount = 0
        for order_item in self.order_items.all():
            total_amount += order_item.calculate_total_amount()
        return total_amount

    def get_total_bonus_amount(self):
        total_bonus_amount = self.total_bonus_amount
        if total_bonus_amount is None:
            total_bonus_amount = 0
        for order_item in self.order_items.filter(is_bonus=True):
            total_bonus_amount += order_item.total_amount

        return total_bonus_amount

    def calculate_total_after_bonus(self):
        if self.partial_bonus_amount > self.total_amount:
            raise ValueError("Bonus amount exceeds total order amount.")
        return self.total_amount - self.partial_bonus_amount

    def save(self, *args, **kwargs):
        self.total_amount = self.apply_promo_code()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name=_('Заказ'))
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, verbose_name=_('Размер продукта'),
                                     blank=True, null=True)
    topping = models.ManyToManyField(Topping, blank=True, verbose_name=_('Добавки'))
    quantity = models.PositiveIntegerField(verbose_name=_('Количество'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Общая сумма'))
    is_bonus = models.BooleanField(default=False, verbose_name=_('Бонусный продукт'))

    # excluded_ingredient = models.ManyToManyField(Ingredient, blank=True,
    #                                              verbose_name=_('Исключенные ингредиенты'))
    # set = models.ForeignKey(Set, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Сет'))

    class Meta:
        verbose_name = _("Элемент заказа")
        verbose_name_plural = _("Элементы заказа")

    def __str__(self):
        return f"{self.product_size.product.name if self.product_size else self.set.name} ({self.product_size.size if self.product_size else 'Сет'}) - {self.quantity} шт."

    def calculate_total_amount(self):
        if not self.is_bonus:
            total = self.quantity * (self.product_size.get_price() if self.product_size else self.set.get_price())
            for topping in self.topping.all():
                total += topping.price * self.quantity
            return total
        else:
            total = self.quantity * (self.product_size.bonus_price if self.product_size else self.set.bonus_price)
            for topping in self.topping.all():
                total += topping.price * self.quantity
            return total

    def save(self, *args, **kwargs):
        if not self.id:
            self.total_amount = 0
            super().save(*args, **kwargs)
        self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)
        self.order.total_amount = self.order.get_total_amount()
        if self.is_bonus:
            self.order.total_bonus_amount = self.order.get_total_bonus_amount()
        self.order.save()


class DistancePricing(models.Model):
    distance = models.IntegerField(verbose_name=_("Расстояние (м)"))
    price = models.IntegerField(verbose_name=_("Время (мин)"))

    def __str__(self):
        return f"{self.distance} м - {self.price} мин"

    class Meta:
        verbose_name = _("Тариф на расстояние")
        verbose_name_plural = _("Тарифы на расстояния")


class PercentCashback(SingletonModel):
    mobile_percent = models.IntegerField(verbose_name=_("Процент за мобильное приложение"))
    web_percent = models.IntegerField(verbose_name=_("Процент за веб-сайт"))
    min_order_price = models.IntegerField(verbose_name=_("Минимальная сумма заказа"))
    bonus_to_use = models.IntegerField(verbose_name=_("Максимальный процент покрытия бонусами(%)"))

    def __str__(self):
        return f"Процент кэшбека № {self.id}"

    class Meta:
        verbose_name = _("Процент кэшбэка")
        verbose_name_plural = _("Проценты кэшбэка")


class Report(models.Model):
    image = models.ImageField(upload_to='reports/', blank=True, null=True, verbose_name=_("Картинка"))
    description = models.TextField(verbose_name=_("Описание"))
    contact_number = models.CharField(max_length=15, verbose_name=_("Контактный номер"))

    def __str__(self):
        return f"Отчет № {self.id}"

    class Meta:
        verbose_name = _("Отчет")
        verbose_name_plural = _("Отчеты")


class PromoCode(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='Промокод')
    valid_from = models.DateTimeField(verbose_name='Начало действия')
    valid_to = models.DateTimeField(verbose_name='Конец действия')
    discount = models.IntegerField(help_text='Процент скидки', verbose_name='Скидка')
    active = models.BooleanField(default=False, verbose_name='Активен')

    def __str__(self):
        return self.code

    @staticmethod
    def generate_code(length=6):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

    def is_valid(self):
        from django.utils import timezone
        return self.active and self.valid_from <= timezone.now() <= self.valid_to

    class Meta:
        verbose_name = _("Промо Код")
        verbose_name_plural = _("Промо Коды")
