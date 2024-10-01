from modeltranslation.translator import register, TranslationOptions
from .models import StaticPage


@register(StaticPage)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
