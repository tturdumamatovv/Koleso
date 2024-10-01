from modeltranslation.translator import register, TranslationOptions
from .models import (
    Category,
    Product,
    Topping,
    Size,
    Tag,
    Article,
)  # Set,Ingredient


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Topping)
class ToppingTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Size)
class SizeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'text')

# @register(Ingredient)
# class IngredientTranslationOptions(TranslationOptions):
#     fields = ('name',)


# @register(Set)
# class SetTranslationOptions(TranslationOptions):
#     fields = ('name', 'description')
