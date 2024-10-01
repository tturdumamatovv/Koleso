from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import TabularInline, ModelAdmin

from apps.pages.models import (
    Banner,
    Phone,
    StaticPage,
    Email,
    SocialLink,
    PaymentMethod,
    Address,
    Contacts,
    MethodsOfPayment,
    DeliveryConditions,
    OrderTypes,
    MainPage,
    Stories,
    Story
)


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ["title", "type", 'object_link', "is_active", "created_at"]
    list_filter = ["title", "is_active", "created_at"]
    search_fields = ["title", "link", "created_at"]
    date_hierarchy = "created_at"
    fields = (
        "type",
        "product",
        "category",
        "link",
        "title",
        "image_desktop",
        "get_image_desktop",
        "image_mobile",
        "get_image_mobile",
        "is_active",
        "created_at",
    )
    readonly_fields = ("get_image_desktop", "get_image_mobile", "created_at")

    def object_link(self, obj):
        if obj.type == 'category' and obj.category:
            # Ссылка на категорию, предполагается что у категории есть метод get_absolute_url()
            return format_html('<a href="{}">{}</a>', obj.category.get_absolute_url(), obj.category)
        elif obj.type == 'product' and obj.product:
            # Ссылка на продукт, предполагается что у продукта есть метод get_absolute_url()
            return format_html('<a href="{}">{}</a>', obj.product.get_absolute_url(), obj.product)
        elif obj.type == 'link' and obj.link:
            # Прямая внешняя ссылка
            return format_html('<a href="{}">{}</a>', obj.link, obj.link)
        return None  # Возвращаем None, если условия не выполняются

    object_link.short_description = "Ссылка объекта"


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin, TabbedTranslationAdmin):
    exclude = [
        'title',
        'description',
    ]


class PhoneInline(TabularInline):
    model = Phone
    extra = 0


class EmailInline(TabularInline):
    model = Email
    extra = 0


class SocialLinkInline(TabularInline):
    model = SocialLink
    extra = 0


class PaymentMethodLinkInline(TabularInline):
    model = PaymentMethod
    extra = 0


class AddressInline(TabularInline):
    model = Address
    extra = 0


@admin.register(Contacts)
class ContactsAdmin(ModelAdmin):
    pass
    inlines = [PhoneInline, EmailInline, SocialLinkInline, PaymentMethodLinkInline, AddressInline]


class OrderTypesInline(TabularInline):
    model = OrderTypes
    extra = 0


class DeliveryConditionsInline(TabularInline):
    model = DeliveryConditions
    extra = 0


class MethodsOfPaymentInline(TabularInline):
    model = MethodsOfPayment
    extra = 0


@admin.register(MainPage)
class MainPageAdmin(ModelAdmin):
    list_display = ('phone', 'icon', 'meta_title', 'meta_description', 'meta_image')
    inlines = [OrderTypesInline, DeliveryConditionsInline, MethodsOfPaymentInline]


class StoryInline(TabularInline):
    extra = 0
    model = Story


@admin.register(Stories)
class StoriesAdmin(ModelAdmin):
    inlines = [StoryInline]