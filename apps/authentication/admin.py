from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from unfold.admin import TabularInline, ModelAdmin

from .models import User, UserAddress, BlacklistedAddress, DailyWorkSummary
from apps.orders.models import Order
from .forms import UserCreationForm, UserChangeForm


class OrderInline(TabularInline):
    model = Order
    extra = 0
    classes = ['collapse']
    fields = (
        'restaurant',
        'delivery',
        'order_time',
        'total_amount',
        'total_bonus_amount',
        'user',
        'is_pickup',
        'payment_method',
        'change',
        'order_status',
        'order_source',
        'comment',
    )
    readonly_fields = (
            'restaurant',
            'delivery',
            'order_time',
            'total_amount',
            'total_bonus_amount',
            'user',
            'is_pickup',
            'payment_method',
            'change',
            'order_status',
            'order_source',
            'comment',
    )


@admin.register(UserAddress)
class UserAddressAdmin(ModelAdmin):
    pass


class UserAddressInline(admin.StackedInline):
    model = UserAddress
    extra = 0
    classes = ['collapse']


@admin.register(User)
class UserAdmin(ModelAdmin, UserAdmin):
    form = UserChangeForm  # Форма для изменения пользователя
    add_form = UserCreationForm  # Форма для создания нового пользователя

    list_display = ('phone_number', 'full_name', 'role', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'role')

    fieldsets = (
        (None, {'fields': ('phone_number', 'full_name', 'role', 'password', 'new_password')}),
        (_('Personal info'), {'fields': ('date_of_birth', 'email', 'profile_picture', 'bonus')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_order', 'receive_notifications')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'role', 'password')}
        ),
    )

    search_fields = ('phone_number', 'full_name')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(BlacklistedAddress)
class BlacklistedAddressAdmin(ModelAdmin):
    list_display = ['address', 'added_at']
    search_fields = ['address__city', 'address__apartment_number']


@admin.register(DailyWorkSummary)
class DailyWorkSummaryAdmin(ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'get_total_hours')
    list_filter = ('user', 'date')

    def get_total_hours(self, obj):
        total_hours = obj.total_duration.total_seconds() / 3600  # Конвертируем секунды в часы
        return f"{total_hours:.2f} часов"

    get_total_hours.short_description = "Общее время за день"
