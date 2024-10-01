from urllib.parse import quote

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm


from .models import (
    Restaurant,
    Delivery,
    Order,
    OrderItem,
    DistancePricing,
    TelegramBotToken,
    PercentCashback,
    Report, WhatsAppChat, PromoCode
)
from apps.services.generate_message import generate_order_message


@admin.register(TelegramBotToken)
class TelegramBotTokenAdmin(ModelAdmin):
    pass


@admin.register(WhatsAppChat)
class WhatsAppChatAdmin(ModelAdmin):
    pass


@admin.register(Restaurant)
class RestaurantAdmin(ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'email', 'opening_hours')
    search_fields = ('name', 'address')
    list_filter = ('opening_hours',)


@admin.register(Delivery)
class DeliveryAdmin(ModelAdmin):
    list_display = ('restaurant', 'user_address', 'delivery_time', 'delivery_fee')
    search_fields = ('restaurant__name', 'user_address__city')
    list_filter = ('delivery_time', 'restaurant')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = (
        'id', 'restaurant', 'delivery', 'order_time', 'total_amount', 'link_to_user', 'order_status', 'is_pickup',
        'order_request_button')
    search_fields = ('user__phone_number',)
    list_filter = ('order_time', 'order_status', 'restaurant', 'is_pickup')
    list_display_links = ('id',)
    list_editable = ('order_status',)
    readonly_fields = ('user', 'delivery', 'order_source', 'id',)
    inlines = [OrderItemInline]

    def total_amount(self, obj):
        return obj.get_total_amount()

    total_amount.short_description = 'Общая сумма'

    def link_to_user(self, obj):
        # return 1
        return format_html('<a href="{}">{}</a>', obj.user.get_admin_url() if obj.user else '', obj.user)

    link_to_user.short_description = 'Пользователь'

    def order_request_button(self, obj):
        distance = obj.delivery.distance_km
        delivery_fee = obj.delivery.delivery_fee
        message = generate_order_message(obj, distance, delivery_fee)
        url_encoded_message = quote(message)
        phone = WhatsAppChat.objects.first()
        if not phone:
            return format_html('')
        else:
            phone.whatsapp_number

        link = f'https://wa.me/{phone}?text={url_encoded_message}'
        return format_html(
            f'<a style="color: white; background-color: orange;" class="button" target="_blank" href="{link}">WhatsApp</a>')

    order_request_button.short_description = 'Действие'


@admin.register(DistancePricing)
class DistancePricingInline(ModelAdmin):
    pass


@admin.register(PercentCashback)
class PercentCashbackAdmin(ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    pass


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = ['code', 'discount', 'valid_from', 'valid_to', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']
