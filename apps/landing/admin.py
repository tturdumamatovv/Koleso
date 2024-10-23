from django.contrib import admin
from unfold.admin import TabularInline, ModelAdmin
from .models import (
    MainPageSite, ServiceFeature, ServiceFeatureStep, StaticPage,
    ConvenientFunctionality, ConvenientFunctionalityChapter, PaymentMethod,
    Product, SubProduct
)

class PaymentMethodInline(TabularInline):
    model = PaymentMethod
    extra = 1  # Number of empty forms you want to display

# Inline for ServiceFeatureStep
class ServiceFeatureStepInline(TabularInline):
    model = ServiceFeatureStep
    extra = 1  # Number of empty forms you want to display


@admin.register(ServiceFeature)
class ServiceFeatureAdmin(ModelAdmin):
    inlines = [ServiceFeatureStepInline]
    list_display = ['title', 'subtitle', 'question']
    ordering = ['title']



# Inline for ConvenientFunctionalityChapter
class ConvenientFunctionalityChapterInline(TabularInline):
    model = ConvenientFunctionalityChapter
    extra = 1


class SubProductInline(TabularInline):
    model = SubProduct
    extra = 1


@admin.register(ConvenientFunctionality)
class ConvenientFunctionalityAdmin(ModelAdmin):
    inlines = [ConvenientFunctionalityChapterInline]
    list_display = ['title', 'description']
    ordering = ['title']


@admin.register(MainPageSite)
class MainPageSiteAdmin(ModelAdmin):
    list_display = ['title', 'description']
    ordering = ['title']
    inlines = [PaymentMethodInline]


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin):
    list_display = ['title', 'slug', 'meta_title', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}  # Auto-generate the slug based on the title


@admin.register(PaymentMethod)
class PaymentMethodAdmin(ModelAdmin):
    list_display = ['link', 'main_page_site']
    ordering = ['link']


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name']
    inlines = [SubProductInline]


@admin.register(SubProduct)
class SubProductAdmin(ModelAdmin):
    list_display = ['title', 'price', 'discounted_price', 'link']
    ordering = ['title']
