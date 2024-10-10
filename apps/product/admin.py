from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin, TabularInline
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Size, Category, Product, ProductSize, Topping, Tag, Article  # Set, Ingredient
from .forms import ProductSizeForm
from mptt.admin import DraggableMPTTAdmin


class ExcludeBaseFieldsMixin:
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        base_fields = getattr(self, 'exclude_base_fields', [])
        for field_name in base_fields:
            if field_name in form.base_fields:
                del form.base_fields[field_name]
        return form


@admin.register(Size)
class SizeAdmin(ExcludeBaseFieldsMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    exclude_base_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(ExcludeBaseFieldsMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    exclude_base_fields = ('name',)


class ProductSizeInline(TabularInline):
    model = ProductSize
    form = ProductSizeForm
    extra = 0


@admin.register(Category)
class CategoryAdmin(ModelAdmin, DraggableMPTTAdmin, ExcludeBaseFieldsMixin, TabbedTranslationAdmin):
    search_fields = ('name',)
    exclude_base_fields = ('name', 'description')
    def indented_title(self, obj):
        return format_html(
            '<div style="text-indent:{}px;">{}</div>',
            obj.level * 20,  # Увеличивайте значение для большего отступа
            obj.name
        )
    indented_title.short_description = 'Название'

    list_display = ('tree_actions', 'indented_title',)
    mptt_level_indent = 20

@admin.register(Product)
class ProductAdmin(SortableAdminMixin, ExcludeBaseFieldsMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('order', 'name', 'category', 'description', 'proteins', 'fats', 'carbohydrates', 'shelf_life', 'storage_conditions', 'manufacturer')
    search_fields = ('name',)
    list_filter = ('category',)
    filter_horizontal = ('toppings', 'tags',)  # 'ingredients')
    inlines = [ProductSizeInline]
    exclude_base_fields = ('name', 'description')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'photo', 'is_popular', 'is_new', 'bonuses',
                       'kkal', 'proteins', 'fats', 'carbohydrates', 'composition', 'shelf_life',
                       'storage_conditions', 'manufacturer', 'tags')
        }),
    )


@admin.register(Topping)
class ToppingAdmin(ExcludeBaseFieldsMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    exclude_base_fields = ('name',)


@admin.register(Article)
class ArticleAdmin(ExcludeBaseFieldsMixin, ModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'text')

# @admin.register(Set)
# class SetAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
#     list_display = ('name', 'description')
#     search_fields = ('name', 'description')
#     filter_horizontal = ('products',)
#     list_filter = ('products',)
#     exclude_base_fields = ('name', 'description')


# @admin.register(Ingredient)
# class IngredientAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)
#     exclude_base_fields = ('name',)
